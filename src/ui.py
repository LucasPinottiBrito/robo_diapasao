import cv2


class UI:
    def show_frame(self, frame):
        cv2.imshow("Triage Robot", frame)


    def is_exit_requested(self):
        return cv2.waitKey(1) & 0xFF == ord('q')