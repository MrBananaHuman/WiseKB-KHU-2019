import sys

from elasticsearch import Elasticsearch

from modules.scouter.config import *

class ScouterHandler():
    '''
    Helpper class for client to communicate with Scouter server
    Args:
        addr (string): scouter server address
        size (string): scroll size that client want to get at once
    '''
    def __init__(self, addr=default_addr, size=default_size):
        self.addr = addr
        self.size = size
    
    def search(self, query_body, data_type, max_num_doc=sys.maxsize, preprocess_fnc=None, trim_lower=True, silence=False):
        '''
        Request the data searched by the query on Scouter server
        Args:
            query_body (dict): query to search generated by class method
            data_type (string): newspaper or graphs or summary_by_time
            preprocess_fnc (function): preprocess function to refine responses
        Returns:
            doc_info_list (list): list of searched data that is refined by preprocess_fnc
        '''
        
        #Qassert data_type == 'newspaper' or data_type == 'graphs'
        
        doc_info_list = []
        if preprocess_fnc == None: preprocess_fnc = self._default_preprocess_fnc
            
        cummulated_num_docs = 0
        
        es_client = Elasticsearch(self.addr)
        response = es_client.search(index=data_type,
                                    doc_type='text',
                                    scroll=default_scroll,
                                    size=self.size if self.size < max_num_doc else max_num_doc,
                                    body=query_body)

        doc_info_list += preprocess_fnc(response)
        
        
        # Get metadata
        scroll_id = response['_scroll_id']
        num_scroll = 1
        num_docs = len(response['hits']['hits'])
        cummulated_num_docs += num_docs
        if not silence:
            print("Scroll idx : {} ({} docs)".format(num_scroll, num_docs))
        
        # Scrolling
        while num_docs > 0:
            if cummulated_num_docs >= max_num_doc:
                break
                
            response = es_client.scroll(scroll_id=scroll_id, scroll='10m')
            doc_info_list += preprocess_fnc(response)
            
            num_scroll += 1
            scroll_id = response['_scroll_id']
            num_docs = len(response['hits']['hits'])
            cummulated_num_docs += num_docs
            if num_docs != 0 and not silence:
                print("Scroll idx : {} ({} docs)".format(num_scroll, num_docs))
            
        if not silence and trim_lower and cummulated_num_docs < max_num_doc:
            print("Trim lower 70% of docs ({} docs are cut)".format(int(len(doc_info_list)*0.3)))
            doc_info_list = doc_info_list[:int(len(doc_info_list)*0.7)]
        
        if not silence:
            print("Total retrieved Doc # : ", len(doc_info_list))
            print()        
        
        return doc_info_list
    
    def search_for_trend(self, query_body, max_num_doc=10000, preprocess_fnc=None, trim_lower=False):
        '''
        Request the data searched by the query on Scouter server
        Args:
            query_body (dict): query to search generated by class method
            data_type (string): newspaper or graphs
            preprocess_fnc (function): preprocess function to refine responses
        Returns:
            doc_info_list (list): list of searched data that is refined by preprocess_fnc
        '''
        
        doc_info_list = []
        if preprocess_fnc == None: preprocess_fnc = self._default_preprocess_fnc
            
        cummulated_num_docs = 0
        
        es_client = Elasticsearch(self.addr)
        response = es_client.search(index='newspaper',
                                    doc_type='text',
                                    scroll='10m',
                                    size=max_num_doc,
                                    body=query_body)
        return response
   
    @classmethod
    def make_keyword_query_body(self, keyword, filters=None):
        '''
        Make a query body with keyword string
        Args:
            keyword (string): additional matching condition
            filters (list): list of fields to be asked
        Returns:
            query_body (dict): query body to be used on elasticsearch
        '''
        
        print("Query : {}".format(keyword))
        keyword_list = keyword.split(' ')
        
        # make a conjugated filter for elasticsearch
        and_query = [{ "match": { "extContent": word } } for word in keyword_list]
        query_body = { 'query': {"bool": {"must":and_query} } }
        if filters is not None:
            query_body['_source'] = filters
        
        return query_body
    
    
    @classmethod
    def make_doc_id_query_body(self, doc_id_list, filters=None):
        '''
        Make a query body with keyword string
        Args:
            doc_id_list (list): doc id list
            filters (list): list of fields to be asked
        Returns:
            query_body (dict): query body to be used on elasticsearch
        '''
        
        # make a conjugated filter for elasticsearch
        #or_query = { "match": { "query": doc_id_list}, "fields": ["news_id"] }
        or_query = { "constant_score": {"filter": { "terms": { "news_id": doc_id_list } } } }
        query_body = { 'query': or_query }
        if filters is not None:
            query_body['_source'] = filters
        
        return query_body
    
    @classmethod
    def make_count_query_body(self, keyword, filters=None):
        '''
        Make a query body to generate trend analysis
        Args:
            opts (dict): additional matching condition
            filters (list): list of fields to be asked
        Returns:
            query_body (dict): query body to be used on elasticsearch
        '''
        
        print("Query : {}".format(keyword))
        keyword_list = keyword.split(' ')
        
        # make a conjugated filter for elasticsearch
        and_query = [{"match": { "extContent": word } } for word in keyword_list]
        query_body = {
            'size':0,
            'query': {"bool": {"must":and_query} },
            "aggs": {
                "group_by_date" :{
                    "date_histogram": {
                        "field": "postingDate",
                        "interval": "1d", 
                        "format": "yyyy-MM-dd"
                    }
                }
            }
        }
        if filters is not None:
            query_body['_source'] = filters
        
        return query_body
    
    def _default_preprocess_fnc(self, response):
        '''
        Default preprocess function that gather relevance score and all fields of data
        '''
        
        doc_info_list = []
        for data in response['hits']['hits']:
            doc_info = data['_source']
            doc_info['rel_score'] = data['_score']
            doc_info_list.append(doc_info)
        return doc_info_list