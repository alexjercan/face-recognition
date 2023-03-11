import asyncio
import json
import logging
import os
import struct

import face_recognition
import numpy as np
from websockets import serve


def read_image(path: str) -> np.ndarray:
    return face_recognition.load_image_file(path)


class Recognition:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []

    def add_face(self, rgb_image: np.ndarray, name: str):
        face_encoding = face_recognition.face_encodings(rgb_image)[0]

        self.known_face_encodings.append(face_encoding)
        self.known_face_names.append(name)

    def detect(self, rgb_image: np.ndarray):
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(
                self.known_face_encodings, face_encoding
            )
            name = "Unknown"

            face_distances = face_recognition.face_distance(
                self.known_face_encodings, face_encoding
            )
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]

            face_names.append(name)

        return face_locations, face_names


def create_face_recognition(whitelist_path: str, logger):
    recognition = Recognition()

    logger.info("initialize recognition model...")
    for name in os.listdir(whitelist_path):
        path = os.path.join(whitelist_path, name)
        for file in os.listdir(path):
            image_path = os.path.join(path, file)
            image = read_image(image_path)

            logger.debug(f"-> added {file} image for {name}")
            recognition.add_face(image, name)
    logger.info("initialize recognition model done")

    async def face_recognition_fn(websocket):
        logger.info("Connection incoming...")
        async for message in websocket:
            logger.debug(f"-> received message of size {len(message)}")

            (height,) = struct.unpack("<I", message[0:4])
            (width,) = struct.unpack("<I", message[4:8])
            frame = np.frombuffer(message[8:], dtype=np.uint8).reshape(
                height, width, -1
            )

            face_locations, face_names = recognition.detect(frame)

            response = {"face_locations": face_locations, "face_names": face_names}

            data = json.dumps(response)
            await websocket.send(data)

    return face_recognition_fn


async def main():
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    whitelist_path = "whitelist"

    logger.info("starting application")

    face_recognition_fn = create_face_recognition(whitelist_path, logger)
    async with serve(face_recognition_fn, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
