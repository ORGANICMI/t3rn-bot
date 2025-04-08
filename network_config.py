# network_config.py

networks = {
    'arb': {
        'name': 'Arbitrum Sepolia',
        'rpc_url': 'https://sepolia.arbitrum.io',
        'chain_id': 421614,
        'contract_address':
        '0x22B65d0B9b59af4D3Ed59F18b9Ad53f5F4908B54'
    },
    'op': {
        'name': 'OP Sepolia',
        'rpc_url': 'https://endpoints.omniatech.io/v1/op/sepolia/public',
        'chain_id': 11155420,
        'contract_address':
        '0xb6Def636914Ae60173d9007E732684a9eEDEF26E'
    },
    'base': {
        'name': 'Base Sepolia',
        'rpc_url': 'https://base-sepolia-rpc.publicnode.com',
        'chain_id': 84532,
        'contract_address': '0xCEE0372632a37Ba4d0499D1E2116eCff3A17d3C3'
    },
    'blast': {
        'name': 'Blast Sepolia',
        'rpc_url': 'https://sepolia.blast.io',
        'chain_id': 168587773,
        'contract_address': '0x9f3871ED60E0C611b751ca2D9F4DCfE1a719A9eB'
    },
    'uni': {
        'name': 'Unichain Sepolia',
        'rpc_url': 'https://unichain-sepolia.drpc.org',
        'chain_id': 1301,
        'contract_address': '0x1cEAb5967E5f078Fa0FEC3DFfD0394Af1fEeBCC9'
    }
}
