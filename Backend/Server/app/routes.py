import asyncio
import json
import os
from flask import request, jsonify, send_from_directory, after_this_request, abort
from app import app
from app import fcm_manager
from app import consumer
from app.regexStripper import regexStripper as res

from app.database_operations import DatabaseOperations

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update

import hashlib
from models import Message


@app.route('/screenshots/<path:filename>')
def serve_image(filename):
    current_dir = os.getcwd()
    image_directory = os.path.join(current_dir, 'public', 'screenshots')
    default_image = 'not_found.png'
    image_path = os.path.join(image_directory, filename)
    default_image_path = os.path.join(image_directory, default_image)

    if not os.path.exists(image_path):
        app.logger.debug("Image does not exist, serving default image.")
        if os.path.exists(default_image_path):
            app.logger.debug("Default image found, serving default image.")
            return send_from_directory(image_directory, default_image)
        else:
            app.logger.error("Default image not found at: %s", default_image_path)
            return "Default image not found.", 404

    app.logger.debug("Image exists, serving image.")
    try:
        return send_from_directory(image_directory, filename)
    except FileNotFoundError:
        app.logger.error("FileNotFoundError: Image not found.")
        abort(404)

@app.route('/analysis', methods=['POST'])
def messageAnalysis():
    data = request.json
    print(f"Received message from client {data}")
    client_registration_id = data.get('registration_id')
    messageId = data.get('localMessageID')
    message = data.get('message')
    threshold_score = 60
    dangerous_score = 70
    safe_score = 30
    
    db_ops = DatabaseOperations()

    async def process_message():
        message_no_links, _ = res.link_stripper(message)
        message_hash = generate_hash(message_no_links)
        needs_analysis = False
        message_data = None
        async with db_ops.SessionLocal() as session:
            async with session.begin():
                existing_message = await db_ops.get_message(message_hash)
                
                if existing_message:
                    if existing_message.status == 'unknown':
                        needs_analysis = True
                    else:
                        message_data = existing_message
                    query = (
                        update(Message)
                        .where(Message.message_hash == message_hash)
                        .values(amount=Message.amount + 1)
                    )
                    await session.execute(query)
                else:
                    needs_analysis = True
                    await db_ops.add_message(message_hash, 'unknown')
                await db_ops.add_user_message(client_registration_id, messageId, message_hash)
        
        if needs_analysis:
            analyzed_message = await consumer.analyze_message_rpc(message)
            final_score = analyzed_message.get('final_score', 0)
            status = 'dangerous' if final_score > threshold_score else 'safe'
            links_json = find_links(message)
            screenshots_json = await get_screenshots(links_json)
            data = {
                "localMessageID": messageId,
                "analyzedMessage": analyzed_message,
                "links": links_json,
                "screenshots": screenshots_json
            }
            async with db_ops.SessionLocal() as session:
                async with session.begin():
                    await db_ops.update_message_status(message_hash, status)
        else:
            links_json = find_links(message)
            screenshots_json = await get_screenshots(links_json)
            data = {
                "localMessageID": messageId,
                "analyzedMessage": dangerous_score if message_data.status == 'dangerous' else safe_score,
                "links": links_json,
                "screenshots": screenshots_json
            }
        fcm_manager.pushToClient(client_registration_id, {"data": data})
    asyncio.run(process_message())
    return jsonify(status="success"), 200


def find_links(message):
    _, links = res.link_stripper(message)
    print(f"Links found: {links}")
    links_dict = {}
    for i in range(len(links)):
        links_dict[f'link{i}'] = links[i]
    return links_dict

async def get_screenshots(links):
    screenshots_dict = {}
    tasks = []

    async def take_screenshot_task(url, key):
        try:
            screenshot_filename = await consumer.take_screenshot_rpc(url)
            screenshots_dict[key] = screenshot_filename if screenshot_filename is not None else "error"
        except Exception as e:
            screenshots_dict[key] = "error"
    for i, link in enumerate(links.values()):
        key = f'link{i}'
        tasks.append(take_screenshot_task(link, key))
    await asyncio.gather(*tasks)
    return screenshots_dict

def generate_hash(message):
    return hashlib.sha256(message.encode()).hexdigest()