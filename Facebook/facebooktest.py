import facebook 

token = 'EAAI7Mrr8DhABAAtwDaGnauuAuUbPlUd3X5LlsFfyDu1C99GHkRo1mZB5NGU1iZBECU9iA9xNj3cKLUrZCxMPh0gDVTauVu4Mxx9iedQg52NBywJswcOZAfOIZC1cGSPX9EDYMlJ0D48T4yg5Iz7xGDC0B3ZAeWoqALNMZCXOFvyMgRaLS3I8ThuUNPAPZA0bebZA77fjJCcVx6I0tUn5ayrNX'
fb = facebook.GraphAPI(access_token = token)
fb.put_object(parent_object = 'me', connection_name = 'feed', message = 'BASZL is on pace!')
# fb.put_wall_post('')
# new token made on 11/17/21