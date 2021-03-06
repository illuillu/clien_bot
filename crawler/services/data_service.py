
from itertools import groupby

from pymongo import MongoClient


class DataService(object):
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client['clien_bot']
        # collection은 게시판 별로 (지금은 allsell으로 고정)
        self.collections = ['allsell']
        self.crawl_collection = self.db['crawl_info']
        print(self.crawl_collection)

    def insert_new_crawl_info(self, board, url):
        return self.crawl_collection.insert_one({
            'board': board, 'url': url, 'latest_sn': 0
        }).inserted_id

    def select_crawl_info(self, board):
        return self.crawl_collection.find_one({'board': board})

    def select_latest_sn(self, board):
        crawl_info = self.select_crawl_info(board)
        if crawl_info is not None and 'latest_sn' in crawl_info:
            return crawl_info['latest_sn']
        else:
            return None

    def update_latest_sn(self, board, latest_sn):
        updated = self.crawl_collection.find_one_and_update(
            {'board': board}, {'$set': {'latest_sn': latest_sn}})
        return updated['_id']

    def select_all_chat_ids(self):
        # 모든 chat_id 가져오기 (공지 발송용)
        chat_ids = []
        for board in self.collections:
            collection = self.db[board]
            for item in collection.find():
                chat_ids.append(item['chat_id'])
        # remove duplication
        return list(set(chat_ids))

    # {'chat_id': xxx, 'keywords': []} 형태를 {'keyword': xxx, 'chat_ids': []}로 변경
    def pivot_all(self, board):
        collection = self.db[board]
        raw_list = []
        for item in collection.find():
            for keyword in item['keywords']:
                raw_list.append({'keyword': keyword, 'chat_id': item['chat_id']})

        raw_list = sorted(raw_list, key=lambda x: x['keyword'])
        pivot_list = []
        for k, group in groupby(raw_list, lambda x: x['keyword']):
            pivot_list.append({
                'keyword': k,
                'chat_ids': [m['chat_id'] for m in group]
            })
        return pivot_list
