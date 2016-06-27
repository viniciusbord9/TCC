import cv2
from common import draw_str, RectSelector
from tracker import Tracker
import video

class Capture:
    def __init__(self, video_src, paused = False):
        self.cap = video.create_capture(video_src)
        _, self.frame = self.cap.read()
        cv2.imshow('frame', self.frame)
        self.rect_sel = RectSelector('frame', self.onrect)
        self.trackers = []
        self.paused = paused

    def onrect(self, rect):
        frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        tracker = Tracker(frame_gray, rect)
        self.trackers.append(tracker)

    def run(self):
        if not self.paused:
            ret, self.frame = self.cap.read()
            if not ret:
                return
            frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            for tracker in self.trackers:
                tracker.update(frame_gray)

        vis = self.frame.copy()
        for tracker in self.trackers:
            tracker.draw_state(vis)
        if len(self.trackers) > 0:
            cv2.imshow('tracker state', self.trackers[-1].state_vis)
        self.rect_sel.draw(vis)

        cv2.imshow('frame', vis)
        ch = cv2.waitKey(10) & 0xFF
        if ch == 27:
            return
        if ch == ord(' '):
            self.paused = not self.paused
        if ch == ord('c'):
            self.trackers = []
