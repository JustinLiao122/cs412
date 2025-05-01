# File: project/search_client.py
# Author: Justin Liao (liaoju@bu.edu), 4/26/2025
# Description: Bonsai APi 


from elasticsearch import Elasticsearch

#  Bonsai Api
es = Elasticsearch(
    "https://gk9ugqs47e:v3c7u7aw8u@personal-search-1930528175.us-east-1.bonsaisearch.net:443",
    verify_certs=True,
)