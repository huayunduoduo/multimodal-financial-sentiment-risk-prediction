import subprocess
import os
import threading  # 添加threading模块导入
import sys

# 定义运行脚本的函数
def run_script(script_path):
    """运行指定的Python脚本"""
    try:
        # 获取脚本所在目录
        script_dir = os.path.dirname(script_path)
        # 获取脚本文件名
        script_name = os.path.basename(script_path)
        
        print(f'开始运行脚本: {script_name}')
        
        # 使用subprocess运行脚本，设置工作目录为脚本所在目录
        process = subprocess.Popen(
            [sys.executable, script_name],
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True  # 在Windows上使用shell=True可能有助于解决路径问题
        )
        
        # 实时输出脚本的标准输出和错误输出
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print(f'脚本 {script_name} 运行成功')
            if stdout:
                print(f'{script_name} 输出: {stdout[:200]}...')  # 只显示前200个字符
        else:
            print(f'脚本 {script_name} 运行失败，返回代码: {process.returncode}')
            if stderr:
                print(f'{script_name} 错误: {stderr[:500]}...')  # 只显示前500个字符
    except Exception as e:
        print(f'运行脚本 {os.path.basename(script_path)} 时发生异常: {str(e)}')

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 定义要运行的脚本列表（使用绝对路径）
scripts = [
    os.path.join(current_dir, '东方财富网股市实战、上证指数吧','上证指数吧.py'),
    os.path.join(current_dir, '东方财富网股市实战、上证指数吧','股市实战吧.py'),
]

# 检查文件是否存在
for script in scripts:
    if not os.path.exists(script):
        print(f'文件 {script} 不存在，请检查路径和文件名。')
    else:
        print(f'找到脚本: {script}')

# 创建线程列表
threads = []
for script in scripts:
    # 为每个脚本创建一个线程
    thread = threading.Thread(target=run_script, args=(script,))
    threads.append(thread)
    # 启动线程
    thread.start()

# 等待所有线程完成
for thread in threads:
    thread.join()

print('所有脚本运行完成')