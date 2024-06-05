from .lesson import Lesson

class Day():
    def __init__(self) -> None:
        self._lessons = []
    
    def add_lesson(self, lesson: Lesson) -> None:
        """ adds a lesson and sorts the array immediately after in ascending order

        Args:
            lesson (Lesson): lesson to add

        """
        self._lessons.append(lesson)
        self._lessons.sort()
    
    def remove_lesson(self, idx: int) -> None:
        """ removes a lesson from the array

        Args:
            idx (int): index of the lesson to remove
        
        Raises:
            IndexError: if idx is out of bounds

        """
        self._lessons.pop(idx)
    
    def get_lessons(self) -> list[Lesson]:
        """ returns the list of lessons

        Returns:
            list[Lesson]: list of lessons

        """
        return self._lessons
    
    def get_lesson(self, idx: int) -> Lesson:
        """ returns the lesson at the specified index

        Args:
            idx (int): index of the lesson to return

        Returns:
            Lesson: lesson at the specified index

        Raises:
            IndexError: if idx is out of bounds

        """
        return self._lessons[idx]