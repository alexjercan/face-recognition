import asyncio
import json
import struct

import cv2
from websockets import connect


async def check_frame(websocket, frame):
    data = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)[..., ::-1]
    height, width, _ = data.shape
    data = struct.pack("<I", height) + struct.pack("<I", width) + data.tobytes()
    await websocket.send(data)
    response = await websocket.recv()
    response = json.loads(response)

    face_locations = response["face_locations"]
    face_names = response["face_names"]

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        cv2.rectangle(
            frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED
        )
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(
            frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1
        )


async def webcam(websocket):
    video_capture = cv2.VideoCapture(0)

    fgbg = cv2.createBackgroundSubtractorMOG2()

    while True:
        _, frame = video_capture.read()

        fgmask = fgbg.apply(frame)

        _, thresh = cv2.threshold(fgmask, 100, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if any(cv2.contourArea(cnt) > 1000 for cnt in contours):
            await check_frame(websocket, frame)

        cv2.imshow("Video", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_capture.release()
    cv2.destroyAllWindows()


async def main(uri):
    async with connect(uri) as websocket:
        await webcam(websocket)


if __name__ == "__main__":
    asyncio.run(main("ws://localhost:8765"))
