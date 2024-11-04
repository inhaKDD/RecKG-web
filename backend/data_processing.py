import pandas as pd
import numpy as np
import json
import math
from copy import deepcopy
from yaml import full_load
from ast import literal_eval

with open('config.yml') as f:
    config = full_load(f)

RELATION = {
    "user": {"age": "agels", "gender": "genderIs", "occupation": "workAs", "residence": "residingAt"},
    "item": {"performer": "performedBy", "type": "typeOf", "release_date": "releasedIn"},
    "interaction": {"rating": "rated"}
}


class DataProcessing:
    def __init__(self, mapping_data):
        self.mapping_data = mapping_data
        self.DATA_PATH = f"{config['storage_path']}/{mapping_data['id']}"
        self.USER_COLUMNS = list(mapping_data['user_data'].keys())
        self.ITEM_COLUMNS = list(mapping_data['item_data'].keys())
        self.INTERACTION_COLUMNS = list(mapping_data['interaction_data'].keys())
        self.node_data = []
        self.edge_data = []


    def process_data(self):
        result = self.load_data()
        if result['status'] != 200:
            return result

        result = self.node_data_processing()
        if result['status'] != 200:
            return result

        result = self.edge_data_processing()
        if result['status'] != 200:
            return result

        result = self.save_json()
        if result['status'] != 200:
            return result
        
        return {"status": 200}

    def load_data(self):
        try:
            self.user_file = pd.read_csv(f"{self.DATA_PATH}/user_file.csv")
            self.item_file = pd.read_csv(f"{self.DATA_PATH}/item_file.csv")
            self.interaction_file = pd.read_csv(f"{self.DATA_PATH}/interaction_file.csv")
            return {"status": 200}
        except Exception as e:
            return {"status": 400, "error": "Couldn't load data file", "details": str(e)}

    def save_json(self):
        try:
            with open(f'{self.DATA_PATH}/node.json', 'w', encoding='utf-8') as f:
                json.dump(self.node_data, f, ensure_ascii=False, indent=4)
            with open(f'{self.DATA_PATH}/edge.json', 'w', encoding='utf-8') as f:
                json.dump(self.edge_data, f, ensure_ascii=False, indent=4)
            return {"status": 200}
        except Exception as e:
            return {"status": 400, "error": "Couldn't save data file", "details": str(e)}
        

    def node_data_processing(self):
        try:
            unique_nodes = set()
            
            # Process user data
            for column in self.USER_COLUMNS:
                col_data = self.mapping_data['user_data'].get(column)
                if col_data:
                    for item in self.user_file[col_data]:
                        if isinstance(item, float) and math.isnan(item):
                            item = "None"
                        data = {"id": item, "type": column}
                        if (data["id"], data["type"]) not in unique_nodes:
                            self.node_data.append(data)
                            unique_nodes.add((data["id"], data["type"]))

            has_item_name = self.mapping_data['item_data'].get('item_name')
            for column in self.ITEM_COLUMNS:
                col_data = self.mapping_data['item_data'].get(column)
                if col_data and column != 'item_name':
                    if column == 'item_id' and has_item_name:
                        ITEM_NAME_COLUMN = self.mapping_data['item_data']['item_name']
                        for idx, item in enumerate(self.item_file[col_data]):
                            if isinstance(item, float) and math.isnan(item):
                                item = "None"
                            items = [item] if not (isinstance(item, str) and item.startswith('[')) else literal_eval(item)
                            for item in items:
                                item_name = self.item_file[ITEM_NAME_COLUMN][idx]
                                
                                if isinstance(item_name, float) and math.isnan(item_name):
                                    item_name = "None"
                                data = {"id": item, "type": column, "data": {"item_name": item_name}}
                                if (data["id"], data["type"]) not in unique_nodes:
                                    self.node_data.append(data)
                                    unique_nodes.add((data["id"], data["type"]))
                    else:
                        for item in self.item_file[col_data]:
                            if isinstance(item, float) and math.isnan(item):
                                item = "None"
                            items = [item] if not (isinstance(item, str) and item.startswith('[')) else literal_eval(item)
                            for item in items:
                                data = {"id": item, "type": column}
                                if (data["id"], data["type"]) not in unique_nodes:
                                    self.node_data.append(data)
                                    unique_nodes.add((data["id"], data["type"]))

            if self.mapping_data['interaction_data']['interaction_list']:
                for column in self.mapping_data['interaction_data']['interaction_list']:
                    for item in self.interaction_file[column]:
                        if isinstance(item, float) and math.isnan(item):
                            item = "None"
                        data = {"id": item, "type": column}
                        if (data["id"], data["type"]) not in unique_nodes:
                            self.node_data.append(data)
                            unique_nodes.add((data["id"], data["type"]))

            return {"status": 200}
        except Exception as e:
            return {"status": 400, "error": "Node data processing error", "details": str(e)}

 #   def node_data_processing(self):
        try:
            unique_nodes = set()
            for column in self.USER_COLUMNS:
                col_data = self.mapping_data['user_data'].get(column)
                if col_data:
                    for item in self.user_file[col_data].dropna():
                        data = {"id": item, "type": column}
                        if (data["id"], data["type"]) not in unique_nodes:
                            self.node_data.append(data)
                            unique_nodes.add((data["id"], data["type"]))

            has_item_name = self.mapping_data['item_data'].get('item_name')
            for column in self.ITEM_COLUMNS:
                col_data = self.mapping_data['item_data'].get(column)
                if col_data and column != 'item_name':
                    if column == 'item_id' and has_item_name:
                        ITEM_NAME_COLUMN = self.mapping_data['item_data']['item_name']
                        for idx, item in enumerate(self.item_file[col_data].dropna()):
                            items = [item] if not (isinstance(item, str) and item.startswith('[')) else literal_eval(item)
                            for item in items:
                                
                                data = {"id": item, "type": column, "data": {"item_name": self.item_file[ITEM_NAME_COLUMN][idx]}}
                                if (data["id"], data["type"]) not in unique_nodes:
                                    self.node_data.append(data)
                                    unique_nodes.add((data["id"], data["type"]))
                    else:
                        for item in self.item_file[col_data].dropna():
                            items = [item] if not (isinstance(item, str) and item.startswith('[')) else literal_eval(item)
                            for item in items:
                                data = {"id": item, "type": column}
                                if (data["id"], data["type"]) not in unique_nodes:
                                    self.node_data.append(data)
                                    unique_nodes.add((data["id"], data["type"]))


            if self.mapping_data['interaction_data']['interaction_list']:
                for column in self.mapping_data['interaction_data']['interaction_list']:
                    for item in self.interaction_file[column].dropna():
                        data = {"id": item, "type": column}
                        if (data["id"], data["type"]) not in unique_nodes:
                            self.node_data.append(data)
                            unique_nodes.add((data["id"], data["type"]))
            return {"status": 200}
        except Exception as e:
            return {"status": 400, "error": "Node data processing error", "details": str(e)}

    def edge_data_processing(self):
        try:
            for column in self.USER_COLUMNS[1:]:
                col_data = self.mapping_data['user_data'].get(column)
                if col_data:
                    for idx, item in enumerate(self.user_file[col_data].dropna()):
                        items = [item] if not (isinstance(item, str) and item.startswith('[')) else literal_eval(item)
                        source = self.user_file[self.mapping_data['user_data']['user_id']][idx]
                        for target in items:
                            data = {"id": f"{source}_{target}", "source": {"type": column, "data": source}, "target": {"type": column, "data": target}, "target": target, "data": {"relation": RELATION['user'][column]}}
                            self.edge_data.append(data)
            
            for column in self.ITEM_COLUMNS[1:]:
                col_data = self.mapping_data['item_data'].get(column)
                if col_data and (column != 'item_name'):
                    for idx, item in enumerate(self.item_file[col_data].dropna()):
                        items = [item] if not (isinstance(item, str) and item.startswith('[')) else literal_eval(item)
                        source = self.item_file[self.mapping_data['item_data']['item_id']][idx]
                        for target in items:
                            data = {"id": f"{source}_{target}", "source": {"type": "item_id", "data": source}, "target": {"type": column, "data": target}, "data": {"relation": RELATION['item'][column]}}
                            self.edge_data.append(data)

            if self.mapping_data['interaction_data']['rating']:
                for user_id, item_id, rating in zip(
                        self.interaction_file[self.mapping_data['interaction_data']['user_id']],
                        self.interaction_file[self.mapping_data['interaction_data']['item_id']],
                        self.interaction_file[self.mapping_data['interaction_data']['rating']]):
                    data = {"id": f"{user_id}_{item_id}", "source": {"type": "user_id", "data": user_id}, "target": {"type": "item_id", "data": item_id}, "data": {"rating": rating}}
                    self.edge_data.append(data)
            return {"status": 200}
        except Exception as e:
            return {"status": 400, "error": "Edge data processing error", "details": str(e)}