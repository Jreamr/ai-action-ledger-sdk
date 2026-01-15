from action_ledger import LedgerClient

client = LedgerClient('http://localhost:8000', 'dev-api-key-change-me')

# Log a test event
result = client.log_event(
    agent_id='sdk-test',
    action_type='test_call',
    input_hash=client.hash_content('hello world'),
    output_hash=client.hash_content('response here')
)
print('Event logged:', result['event_id'])

# Verify the chain
verify = client.verify_chain('sdk-test')
print('Chain valid:', verify['is_valid'])