# generate_token.py
import jwt
import time

JWT_SECRET = 'your_jwt_secret'  # Must match with the one in main.py
JWT_ALGORITHM = 'HS256'

def generate_token(company_id, user_id, role):
    payload = {
        'company_id': company_id,
        'user_id': user_id,
        'role': role,
        'exp': int(time.time()) + 3600  # Token valid for 1 hour
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    print(f"Token for {role} '{user_id}' in company '{company_id}':\n{token}\n")

# Example usage:
if __name__ == '__main__':
    # Tokens for CompanyA
    generate_token('CompanyA', 'user1', 'user')
    generate_token('CompanyA', 'user2', 'user')
    generate_token('CompanyA', 'admin1', 'admin')

    # Tokens for CompanyB
    generate_token('CompanyB', 'user3', 'user')
    generate_token('CompanyB', 'admin2', 'admin')
