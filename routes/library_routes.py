from flask import Blueprint, jsonify, request, send_file
from services.search_service import search_prompts
import json, os

library_bp = Blueprint('library', __name__)
DATA_FILE = 'data/prompts.json'

currentSearch = []

def sortAZ(prompt):
    return prompt["purpose"]

def sortScore(prompt):
    return prompt["score"]["total"], prompt["purpose"]

def sortTone(prompt):
    return prompt["tone_label"], prompt["purpose"]

def createSortedSearchData(sort, descending):
    #data = request.get_json()
    #keyword = data.get('keyword', '')
    results = currentSearch.copy() # search_prompt(read_date(), keyword)
    results.sort(key = sort, reverse = descending)
    return jsonify(results)

def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f: return json.load(f)

@library_bp.route('/library', methods=['GET'])
def library():
    global currentSearch
    currentSearch = read_data()
    return jsonify(currentSearch) #jsonify(read_data())

@library_bp.route('/library/search', methods=['POST'])
def library_search():
    global currentSearch
    data = request.get_json()
    keyword = data.get('keyword', '')
    results = search_prompts(read_data(), keyword)
    
    currentSearch = results
    
    return jsonify(results)

@library_bp.route('/library/sortAZ', methods=['POST'])
def library_sortAZ():
    return createSortedSearchData(sortAZ, True)

@library_bp.route('/library/sortScore', methods = ['POST'])
def library_sortScore():
    return createSortedSearchData(sortScore, True)

@library_bp.route("/library/sortTone", methods = ['POST'])
def library_sortTone():
    return createSortedSearchData(sortTone, True)

@library_bp.route('/library/export')
def export():
    return send_file(DATA_FILE, as_attachment=True)