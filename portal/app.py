import pymongo
from flask import Flask, jsonify, request
from dataclasses import asdict
from ipaddress import IPv4Address, IPv4Network
import logging
from time import sleep

from .data import Site

app = Flask(__name__, static_folder='static')
logger: logging.Logger = app.logger
logger.setLevel(logging.DEBUG)

logger.info("Initializing connection to mongodb...")
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client['portal']
logger.info("Mongodb connection successful")

collection_network_mapping = {
    IPv4Network('1.2.0.0/22', strict=True): 'Mesh'
}


def generate_data():

    logger.debug("Sleeping for 5 seconds")
    sleep(5)

    logger.debug("Listing DB collections...")
    if 'sites' in db.list_collection_names():
        logger.info("'sites' collection exists, will not generate data.")
        return

    logger.info("Generating data...")

    jenkins_site = Site(
        title='Jenkins',
        image_path='images/jenkins.png'
    )

    confluence_site = Site(
        title='Confluence',
        image_path='images/confluence.png'
    )

    logger.debug("Inserting sites to DB")
    jenkins_id, confluence_id = db['sites'].insert_many(map(asdict, (jenkins_site, confluence_site))).inserted_ids

    logger.debug("Inserting collections to DB")
    db['collections'].insert_many((
        {'name': 'Mesh', 'sites': [jenkins_id, confluence_id]},
        {'name': 'General', 'sites': [confluence_id]}
    ))

    logger.info("Data generated successfully")


@app.route('/')
def hello_world():
    user_ip = IPv4Address(request.remote_addr)
    # user_ip = IPv4Address('1.2.3.4')
    logger.info(f'User connected from {user_ip}')

    for network, collection_name in collection_network_mapping.items():
        if user_ip in network:
            return specific_collection(collection_name)

    return specific_collection('General')


def specific_collection(name):
    # Find the collection using the name to get the site_ids
    site_ids = db['collections'].find_one({'name': name}, {'_id': 0, 'sites': 1})['sites']

    # Get the sites from the ids
    sites = db['sites'].find({'_id': {'$in': site_ids}}, {'_id': 0})

    return jsonify(list(sites))


if __name__ == '__main__':
    generate_data()
    app.ses
    app.run()
