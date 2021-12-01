import facebook 

token = 'EAAI7Mrr8DhABALiK49eaOjEsSkWbsZAWMrxXTMgxdfoGt4PzQ9oo7sVZBZAIyJs1Ky966MsGu11gZCNvUxMatdLvNsBnF6jqrc7QrCj6sjN8flf5SNU5NvXKLSQfnUZB8DApJY1FXnsMTXAQ9UXSxuYHZAoH41ZBDCPziU4ZCNKTN4FDhyxXzChR96ZBKMrz6yUicU6kVGZAFwW32fgD1TPTye'
fb = facebook.GraphAPI(access_token = token)
fb.put_object(parent_object = 'me', connection_name = 'feed', message = 'BASZL is on pace!')
# fb.put_wall_post('')
# new token made on 11/17/21