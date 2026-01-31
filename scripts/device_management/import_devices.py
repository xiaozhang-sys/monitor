#!/usr/bin/env python3
"""
设备批量导入工具
支持从CSV文件批量导入监控设备到系统
"""

import csv
import requests
import sys
import os
import json
import logging
import traceback
import time
import argparse
from typing import List, Dict, Optional, Any, Tuple, Type, Callable
import ipaddress

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('device_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径以便导入自定义模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class DeviceImportError(Exception):
    """设备导入过程中的基础异常"""
    pass


class NetworkError(DeviceImportError):
    """网络相关异常"""
    pass


class ValidationError(DeviceImportError):
    """数据验证异常"""
    pass


class APIError(DeviceImportError):
    """API调用异常"""
    pass


class DeviceImporter:
    """设备导入器类，负责批量导入设备信息"""
    
    def __init__(self, api_url: str, timeout: int = 30, verify_ssl: bool = True):
        """
        初始化设备导入器
        
        Args:
            api_url: API服务地址
            timeout: 请求超时时间（秒）
            verify_ssl: 是否验证SSL证书
        """
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.token = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def login(self, username: str, password: str) -> bool:
        """
        登录到系统获取认证令牌
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            bool: 登录是否成功
        
        Raises:
            NetworkError: 网络连接异常
            APIError: API返回错误
        """
        try:
            login_data = {
                'username': username,
                'password': password
            }
            
            logger.info(f"尝试登录到 {self.api_url}")
            response = self.session.post(
                f'{self.api_url}/token',
                data=login_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            if response.status_code != 200:
                raise APIError(f"登录失败: HTTP {response.status_code} - {response.text}")
            
            token_data = response.json()
            if 'access_token' not in token_data:
                raise APIError("响应中未找到访问令牌")
            
            self.token = token_data['access_token']
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
            
            logger.info(f"登录成功，token: {self.token[:20]}...")
            return True
            
        except requests.RequestException as e:
            raise NetworkError(f"网络请求异常: {str(e)}") from e
    
    def import_device(self, device: Dict[str, Any]) -> Dict[str, Any]:
        """
        导入单个设备
        
        Args:
            device: 设备信息字典
            
        Returns:
            Dict: API返回结果
            
        Raises:
            NetworkError: 网络连接异常
            APIError: API返回错误
        """
        try:
            logger.info(f"导入设备: {device.get('name', 'Unknown')} ({device.get('ip', 'Unknown')})")
            response = self.session.post(
                f'{self.api_url}/import', 
                json=device,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            if response.status_code != 200:
                raise APIError(f"设备导入失败: HTTP {response.status_code} - {response.text}")
            
            try:
                result = response.json()
                logger.info(f"设备导入成功: {device.get('name', 'Unknown')}")
                return result
            except json.JSONDecodeError as e:
                raise APIError(f"响应数据不是有效的JSON格式: {str(e)}") from e
                
        except requests.RequestException as e:
            raise NetworkError(f"网络请求异常: {str(e)}") from e
    
    def validate_device_data(self, device: Dict[str, Any]) -> List[str]:
        """
        验证设备数据格式
        
        Args:
            device: 设备信息字典
            
        Returns:
            List[str]: 验证错误信息列表，为空表示验证通过
        """
        errors = []
        
        # 验证必需字段
        required_fields = ['ip', 'user', 'pwd']
        for field in required_fields:
            if field not in device or not device[field]:
                errors.append(f"缺少必需字段: {field}")
        
        # 验证IP地址格式
        if 'ip' in device and device['ip']:
            try:
                ipaddress.ip_address(device['ip'])
            except ValueError:
                errors.append(f"无效的IP地址: {device['ip']}")
        
        # 验证端口号
        if 'port' in device and device['port']:
            try:
                port = int(device['port'])
                if port < 1 or port > 65535:
                    errors.append(f"端口号必须在1-65535之间: {device['port']}")
            except ValueError:
                errors.append(f"无效的端口号: {device['port']}")
        
        # 验证通道数
        if 'chs' in device and device['chs']:
            try:
                chs = int(device['chs'])
                if chs < 1:
                    errors.append(f"通道数必须大于0: {device['chs']}")
            except ValueError:
                errors.append(f"无效的通道数: {device['chs']}")
        
        return errors
    
    def import_from_csv(self, csv_file: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        从CSV文件导入设备
        
        Args:
            csv_file: CSV文件路径
            dry_run: 是否仅进行测试而不实际导入
            
        Returns:
            Dict: 导入结果统计
        
        Raises:
            FileNotFoundError: 文件未找到
            ValidationError: CSV文件格式验证失败
        """
        results = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"文件未找到: {csv_file}")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # 检查必需字段
                required_fields = ['IP地址', '用户名', '密码']
                fieldnames = reader.fieldnames
                if fieldnames is None:
                    raise ValidationError("CSV文件格式错误：缺少列标题")
                    
                missing_fields = [field for field in required_fields if field not in fieldnames]
                if missing_fields:
                    raise ValidationError(f"CSV文件缺少必需字段: {missing_fields}")
                
                logger.info(f"开始从CSV文件导入设备，文件: {csv_file}")
                
                for row_num, row in enumerate(reader, start=2):  # 从第2行开始计数（因为第1行是标题）
                    results['total'] += 1
                    
                    try:
                        # 构建设备信息字典
                        device = {
                            'region': row.get('区域', '默认区域'),
                            'store': row.get('门店', '默认门店'),
                            'ip': row['IP地址'],
                            'port': int(row.get('端口', 554)),
                            'user': row['用户名'],
                            'pwd': row['密码'],
                            'chs': int(row.get('通道数', 1)),
                            'name': row.get('设备名称', f"{row.get('区域', '默认区域')}-{row.get('门店', '默认门店')}-{row['IP地址']}")
                        }
                        
                        # 验证设备数据
                        validation_errors = self.validate_device_data(device)
                        if validation_errors:
                            results['skipped'] += 1
                            error_msg = f"数据验证失败: {'; '.join(validation_errors)}"
                            results['details'].append({
                                'row': row_num,
                                'status': 'skipped',
                                'device': device,
                                'error': error_msg
                            })
                            logger.warning(f"第{row_num}行: {error_msg}")
                            continue
                        
                        # 执行导入或仅模拟
                        if dry_run:
                            results['success'] += 1
                            results['details'].append({
                                'row': row_num,
                                'status': 'dry_run',
                                'device': device,
                                'result': '模拟导入成功'
                            })
                            logger.info(f"第{row_num}行: 模拟导入成功 - {device['name']} ({device['ip']})")
                        else:
                            # 实际导入设备
                            result = self.import_device(device)
                            results['success'] += 1
                            results['details'].append({
                                'row': row_num,
                                'status': 'success',
                                'device': device,
                                'result': result
                            })
                            
                    except (ValueError, KeyError) as e:
                        results['failed'] += 1
                        error_msg = f"数据格式错误: {str(e)}"
                        results['details'].append({
                            'row': row_num,
                            'status': 'error',
                            'device': dict(row) if 'IP地址' in row else {},
                            'error': error_msg
                        })
                        logger.error(f"第{row_num}行: {error_msg}")
                        
                    except Exception as e:
                        results['failed'] += 1
                        error_msg = str(e)
                        results['details'].append({
                            'row': row_num,
                            'status': 'error',
                            'device': dict(row) if 'IP地址' in row else {},
                            'error': error_msg
                        })
                        logger.error(f"第{row_num}行: 导入失败 - {error_msg}")
                        logger.debug(traceback.format_exc())
                        
        except UnicodeDecodeError as e:
            raise ValidationError(f"文件编码错误，请确保使用UTF-8编码: {str(e)}") from e
        
        logger.info(f"设备导入完成 - 总计: {results['total']}, 成功: {results['success']}, 失败: {results['failed']}, 跳过: {results['skipped']}")
        return results


def create_sample_csv(filename: str):
    """
    创建示例CSV文件
    
    Args:
        filename: 输出文件名
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['区域', '门店', 'IP地址', '端口', '用户名', '密码', '通道数', '设备名称'])
            writer.writerow(['北京', '中关村店', '192.168.1.100', '554', 'admin', 'password123', '4', '门口摄像头'])
            writer.writerow(['上海', '南京路店', '192.168.1.101', '554', 'admin', 'password123', '8', '大厅摄像头'])
            writer.writerow(['广州', '天河店', '192.168.1.102', '554', 'admin', 'password123', '2', '收银台'])
        logger.info(f"示例CSV文件已创建: {filename}")
        print(f"✅ 示例CSV文件已创建: {filename}")
    except Exception as e:
        logger.error(f"创建示例CSV文件失败: {str(e)}")
        print(f"❌ 创建示例CSV文件失败: {str(e)}")


def print_import_summary(results: Dict[str, Any]):
    """
    打印导入结果摘要
    
    Args:
        results: 导入结果统计
    """
    print(f"\n📊 导入结果摘要:")
    print(f"   总计: {results['total']}")
    print(f"   成功: {results['success']}")
    print(f"   失败: {results['failed']}")
    print(f"   跳过: {results['skipped']}")
    
    # 打印失败详情
    if results['failed'] > 0:
        print("\n❌ 失败详情:")
        for detail in results['details']:
            if detail['status'] == 'error':
                device_info = detail.get('device', {})
                device_name = device_info.get('name', device_info.get('IP地址', '未知设备'))
                print(f"   行{detail['row']} - {device_name}: {detail.get('error', '未知错误')}")
                
    # 打印跳过详情
    if results['skipped'] > 0:
        print("\n⚠️ 跳过详情:")
        for detail in results['details']:
            if detail['status'] == 'skipped':
                device_info = detail.get('device', {})
                device_name = device_info.get('name', device_info.get('IP地址', '未知设备'))
                print(f"   行{detail['row']} - {device_name}: {detail.get('error', '未知错误')}")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='设备批量导入工具')
    parser.add_argument('csv_file', nargs='?', help='CSV文件路径')
    parser.add_argument('--api-url', default='http://localhost:8000', help='API服务地址 (默认: http://localhost:8000)')
    parser.add_argument('--username', help='登录用户名')
    parser.add_argument('--password', help='登录密码')
    parser.add_argument('--create-sample', action='store_true', help='创建示例CSV文件')
    parser.add_argument('--dry-run', action='store_true', help='仅进行测试而不实际导入')
    parser.add_argument('--timeout', type=int, default=30, help='请求超时时间（秒）')
    parser.add_argument('--no-verify-ssl', action='store_true', help='不验证SSL证书')
    parser.add_argument('--output', help='输出结果到指定文件')
    parser.add_argument('--verbose', action='store_true', help='显示详细日志')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 创建示例CSV文件
    if args.create_sample:
        create_sample_csv('devices_sample.csv')
        return
    
    # 检查CSV文件参数
    if not args.csv_file:
        parser.print_help()
        return
    
    # 检查文件是否存在
    if not os.path.exists(args.csv_file):
        print(f"❌ 文件不存在: {args.csv_file}")
        logger.error(f"文件不存在: {args.csv_file}")
        return
    
    try:
        # 创建导入器实例
        importer = DeviceImporter(
            args.api_url,
            timeout=args.timeout,
            verify_ssl=not args.no_verify_ssl
        )
        
        # 登录
        username = args.username or input("请输入用户名 (默认: admin): ") or 'admin'
        password = args.password or input("请输入密码 (默认: ${DEFAULT_ADMIN_PASSWORD}): ") or os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
        
        importer.login(username, password)
        
        # 导入设备
        start_time = time.time()
        results = importer.import_from_csv(args.csv_file, dry_run=args.dry_run)
        end_time = time.time()
        
        # 打印导入结果
        print_import_summary(results)
        print(f"\n⏱️  总耗时: {end_time - start_time:.2f} 秒")
        
        # 输出结果到文件
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n📄 结果已保存到: {args.output}")
            logger.info(f"结果已保存到: {args.output}")
            
    except Exception as e:
        print(f"❌ 程序执行出错: {str(e)}")
        logger.error(f"程序执行出错: {str(e)}")
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()