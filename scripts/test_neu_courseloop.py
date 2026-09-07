import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('loop', Path(__file__).with_name('neu_courseloop.py'))
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)


class LoopTests(unittest.TestCase):
    def test_fenced_comments_are_not_chapters(self):
        self.assertEqual(loop.headings('# One\n```python\n# Not a chapter\n```\n# Two'),
                         [(0, 1, 'One'), (4, 1, 'Two')])

    def test_tilde_fences(self):
        self.assertEqual(loop.headings('~~~\n# hidden\n~~~\n## Real'), [(3, 2, 'Real')])

    def test_atomic_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'state.json'
            loop.save(path, {'pending':2})
            loop.save(path, {'pending':1})
            self.assertEqual(loop.json.loads(path.read_text()), {'pending':1})
            self.assertFalse(path.with_suffix('.json.tmp').exists())

    def test_missing_receipt_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                loop.verify(Path(directory), {'output':'missing'})

    def test_inventory_and_changed_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'chapters').mkdir()
            (root / 'assignments').mkdir()
            (root / 'chapters/01-example.md').write_text('# Example\n')
            (root / 'lesson.md').write_text('# Lesson\n## Assessments\n1. Build a counter.\n2. Explain it.\n')
            for n in range(10):
                (root / f'assignments/assignment-{n:02}.md').write_text('# Brief\n')
            loop.save(root / 'course.json', {'lessons':[{'lesson':1,'path':'lesson.md'}]})
            loop.save(root / 'neu-courseloop.json', {'assignments_dir':'assignments'})
            (root / 'NEU-COURSELOOP-PROMPT.md').write_text('Liam')
            first = loop.inventory(root)
            self.assertEqual(len(first), 13)
            self.assertEqual([j['kind'] for j in first[:3]], ['chapter','assignment','exercise'])
            self.assertEqual(first, loop.inventory(root))
            (root / 'chapters/01-example.md').write_text('# Example revised\n')
            second = loop.inventory(root)
            self.assertEqual(first[0]['id'], second[0]['id'])
            self.assertNotEqual(first[0]['source_hash'], second[0]['source_hash'])
            self.assertEqual(first[1], second[1])


if __name__ == '__main__':
    unittest.main()
