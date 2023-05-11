import boto3
import json
import pymysql
import os

def lambda_handler(event, context):
    
    # Leitura dos dados da requisição
    token = event['token']
    
    # Conexão com o banco de dados
    secretsmanager = boto3.client('secretsmanager')
    response = secretsmanager.get_secret_value(SecretId=f'replenish4me-db-password-{os.environ.get("env", "dev")}')
    db_password = response['SecretString']
    rds = boto3.client('rds')
    response = rds.describe_db_instances(DBInstanceIdentifier=f'replenish4medatabase{os.environ.get("env", "dev")}')
    endpoint = response['DBInstances'][0]['Endpoint']['Address']
    # Conexão com o banco de dados
    with pymysql.connect(
        host=endpoint,
        user='admin',
        password=db_password,
        database='replenish4me'
    ) as conn:
    
        # Verificação da sessão ativa no banco de dados
        with conn.cursor() as cursor:
            sql = "SELECT usuario_id FROM SessoesAtivas WHERE id = %s"
            cursor.execute(sql, (token,))
            result = cursor.fetchone()
            
            if result is None:
                response = {
                    "statusCode": 401,
                    "body": json.dumps({"message": "Sessão inválida"})
                }
                return response
            
            usuario_id = result[0]
            
            # Leitura dos produtos no carrinho do usuário
            sql = "SELECT CarrinhoCompras.id, Produtos.nome, Produtos.descricao, Produtos.preco, CarrinhoCompras.quantidade FROM CarrinhoCompras INNER JOIN Produtos ON CarrinhoCompras.produto_id = Produtos.id WHERE CarrinhoCompras.usuario_id = %s"
            cursor.execute(sql, (usuario_id,))
            result = cursor.fetchall()
            
            carrinho = []
            total = 0
            
            for row in result:
                produto_id = row[0]
                nome = row[1]
                descricao = row[2]
                preco = row[3]
                quantidade = row[4]
                total += preco * quantidade
                
                carrinho.append({
                    "produto_id": produto_id,
                    "nome": nome,
                    "descricao": descricao,
                    "preco": preco,
                    "quantidade": quantidade
                })
        

    # Retorno da resposta da função
    response = {
        "statusCode": 200,
        "body": json.dumps({
            "carrinho": carrinho,
            "total": total
        })
    }
    return response
