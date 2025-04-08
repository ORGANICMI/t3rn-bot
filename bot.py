# 导入 Web3 库
from web3 import Web3
from eth_account import Account
import time
import sys
import os
import random  # 引入随机模块

# 数据桥接配置
from data_bridge import data_bridge
from keys_and_addresses import private_keys, labels  # 不再读取 my_addresses
from network_config import networks

# 文本居中函数
def center_text(text):
    terminal_width = os.get_terminal_size().columns
    lines = text.splitlines()
    centered_lines = [line.center(terminal_width) for line in lines]
    return "\n".join(centered_lines)

# 清理终端函数
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

description = """
自动桥接机器人  https://unlock3d.t3rn.io/rewards
还是继续操你麻痹Rambeboy,偷私钥🐶  V2版本
"""

# 每个链的颜色和符号（更新为5条链对应的颜色）
chain_symbols = {
    'arb': '\033[34m',      # Arbitrum
    'op': '\033[91m',       # Optimism / OP Sepolia
    'base': '\033[92m',     # Base
    'uni': '\033[93m',      # Uni（例如 Uniswap 或其它）
    'blast': '\033[95m'     # Blast
}

# 颜色定义
green_color = '\033[92m'
reset_color = '\033[0m'
menu_color = '\033[95m'  # 菜单文本颜色

# 每个网络的区块浏览器URL（此处为示例，后续可根据实际情况修改）
explorer_urls = {
    'arb': 'https://arb.explorer.url/tx/',       
    'op': 'https://op.explorer.url/tx/',
    'base': 'https://base.explorer.url/tx/',
    'uni': 'https://uni.explorer.url/tx/',
    'blast': 'https://blast.explorer.url/tx/',
    'b2n': 'https://b2n.explorer.caldera.xyz/tx/'
}

# 获取b2n余额的函数
def get_b2n_balance(web3, my_address):
    balance = web3.eth.get_balance(my_address)
    return web3.from_wei(balance, 'ether')

# 检查链的余额函数
def check_balance(web3, my_address):
    balance = web3.eth.get_balance(my_address)
    return web3.from_wei(balance, 'ether')

# 创建和发送交易的函数
def send_bridge_transaction(web3, account, my_address, data, network_key):
    nonce = web3.eth.get_transaction_count(my_address, 'pending')
    value_in_ether = 0.101
    value_in_wei = web3.to_wei(value_in_ether, 'ether')

    try:
        gas_estimate = web3.eth.estimate_gas({
            'to': networks[network_key]['contract_address'],
            'from': my_address,
            'data': data,
            'value': value_in_wei
        })
        gas_limit = gas_estimate + 50000  # 增加安全边际
    except Exception as e:
        print(f"估计gas错误: {e}")
        return None

    base_fee = web3.eth.get_block('latest')['baseFeePerGas']
    priority_fee = web3.to_wei(5, 'gwei')
    max_fee = base_fee + priority_fee

    transaction = {
        'nonce': nonce,
        'to': networks[network_key]['contract_address'],
        'value': value_in_wei,
        'gas': gas_limit,
        'maxFeePerGas': max_fee,
        'maxPriorityFeePerGas': priority_fee,
        'chainId': networks[network_key]['chain_id'],
        'data': data
    }

    try:
        signed_txn = web3.eth.account.sign_transaction(transaction, account.key)
    except Exception as e:
        print(f"签名交易错误: {e}")
        return None

    try:
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        # 获取最新余额
        balance = web3.eth.get_balance(my_address)
        formatted_balance = web3.from_wei(balance, 'ether')

        # 获取区块浏览器链接
        explorer_link = f"{explorer_urls[network_key]}{web3.to_hex(tx_hash)}"

        # 显示交易信息
        print(f"{green_color}📤 发送地址: {account.address}")
        print(f"⛽ 使用Gas: {tx_receipt['gasUsed']}")
        print(f"🗳️  区块号: {tx_receipt['blockNumber']}")
        print(f"💰 ETH余额: {formatted_balance} ETH")
        b2n_balance = get_b2n_balance(Web3(Web3.HTTPProvider('https://b2n.rpc.caldera.xyz/http')), my_address)
        print(f"🔵 b2n余额: {b2n_balance} b2n")
        print(f"🔗 区块浏览器链接: {explorer_link}\n{reset_color}")

        return web3.to_hex(tx_hash), value_in_ether
    except Exception as e:
        print(f"发送交易错误: {e}")
        return None, None

# 在特定网络上处理交易的函数
def process_network_transactions(network_key, bridges, chain_data, successful_txs):
    web3 = Web3(Web3.HTTPProvider(chain_data['rpc_url']))

    # 如果无法连接，重试直到成功
    while not web3.is_connected():
        print(f"无法连接到 {networks[network_key]['name']}，正在尝试重新连接...")
        time.sleep(5)  # 等待 5 秒后重试
        web3 = Web3(Web3.HTTPProvider(chain_data['rpc_url']))
    
    print(f"成功连接到 {networks[network_key]['name']}")

    for bridge in bridges:
        for i, private_key in enumerate(private_keys):
            account = Account.from_key(private_key)
            my_address = account.address
            data = data_bridge.get(bridge)  # 确保 data_bridge 是字典类型
            if not data:
                print(f"桥接 {bridge} 数据不可用!")
                continue

            result = send_bridge_transaction(web3, account, my_address, data, network_key)
            if result:
                tx_hash, value_sent = result
                successful_txs += 1

                if value_sent is not None:
                    print(f"{chain_symbols[network_key]}🚀 成功交易总数: {successful_txs} | {labels[i]} | 桥接: {bridge} | 桥接金额: {value_sent:.5f} ETH ✅{reset_color}\n")
                else:
                    print(f"{chain_symbols[network_key]}🚀 成功交易总数: {successful_txs} | {labels[i]} | 桥接: {bridge} ✅{reset_color}\n")

                print(f"{'='*150}")
                print("\n")
            
            # 随机等待 120 到 180 秒
            wait_time = random.uniform(120, 180)
            print(f"⏳ 等待 {wait_time:.2f} 秒后继续...\n")
            time.sleep(wait_time)

    return successful_txs

def main():
    # 清屏（可选）
    clear_terminal()
    print("\033[92m" + center_text(description) + "\033[0m")
    print("\n\n")

    # ------------------------------
    # 在此处增加交互式链选择
    # ------------------------------
    chain1 = input("请输入第一条链 (可选: arb, op, base, uni, blast): ").strip().lower()
    chain2 = input("请输入第二条链 (可选: arb, op, base, uni, blast): ").strip().lower()

    if chain1 not in networks or chain2 not in networks:
        print("输入的链名称有误，请在 [arb, op, base, uni, blast] 中选择。")
        sys.exit(1)

    # 显示选择的链配置（每行前有 "    - "）
    print("    - 源链配置：")
    print(f"    -   名称: {networks[chain1]['name']}")
    print(f"    -   RPC: {networks[chain1]['rpc_url']}")
    print("    - 目标链配置：")
    print(f"    -   名称: {networks[chain2]['name']}")
    print(f"    -   RPC: {networks[chain2]['rpc_url']}")
    print("\n")

    # 将选中的链作为当前跨链的两端
    current_network = chain1
    alternate_network = chain2

    successful_txs = 0

    # 循环执行跨链交易
    while True:
        # 检查当前网络余额
        web3 = Web3(Web3.HTTPProvider(networks[current_network]['rpc_url']))
        
        # 如果无法连接，尝试重新连接
        while not web3.is_connected():
            print(f"无法连接到 {networks[current_network]['name']}，正在尝试重新连接...")
            time.sleep(5)
            web3 = Web3(Web3.HTTPProvider(networks[current_network]['rpc_url']))
        
        print(f"成功连接到 {networks[current_network]['name']}")
        
        my_address = Account.from_key(private_keys[0]).address  # 使用第一个私钥的地址
        balance = check_balance(web3, my_address)

        # 如果余额不足 0.101 ETH，则切换到另一条链
        if balance < 0.101:
            print(f"{chain_symbols[current_network]}{networks[current_network]['name']} 余额不足 0.101 ETH，切换到 {networks[alternate_network]['name']}{reset_color}")
            current_network, alternate_network = alternate_network, current_network

        # 构造桥接标签，例如 "ARB -> OP"（这里直接使用键的大写形式）
        bridge_label = f"{current_network.upper()} -> {alternate_network.upper()}"
        successful_txs = process_network_transactions(current_network, [bridge_label], networks[current_network], successful_txs)

        # 自动切换时加入随机延时
        time.sleep(random.uniform(30, 60))

if __name__ == "__main__":
    main()
