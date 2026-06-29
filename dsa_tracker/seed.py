from .models import Section, Topic, db


CURRICULUM = [
( "Programming Fundamentals", "Build the core programming concepts required before starting Data Structures & Algorithms. These concepts are language-independent and can be learned using Java, Python, C++, C#, JavaScript, or any modern programming language.",
  [ "Variables, Data Types & Input/Output",
    "Operators & Expressions",
    "Conditional Statements (Decision Making)",
    "Loops & Iteration", "Functions & Modular Programming",
    "Time Complexity Basics (Introduction to Big-O)",
    "Arrays (1D & 2D)",
    "Dynamic Arrays / Lists",
    "Strings",
    "Hash Maps / Dictionaries (Basic Usage)"
    ],
  ),
    (
        "Intermediate DSA",
        "Build problem-solving fundamentals and core data structure techniques.",
        [
            "Introduction to Problem Solving",
            "Time Complexity",
            "Introduction to Arrays",
            "Arrays: Prefix Sum",
            "Arrays: Carry Forward & Subarrays",
            "Arrays: Sliding Window & Contribution Technique",
            "Arrays: 2D Matrices",
            "Memory Management",
            "Sorting Basics",
            "Bit Manipulation Basics",
            "Strings",
            "Interview Problems",
        ],
    ),
    (
        "Advanced DSA 1",
        "Strengthen arrays, recursion, bit manipulation, and backtracking.",
        [
            "Arrays 1: One Dimensional",
            "Arrays 2: Two Dimensional",
            "Arrays 3: Interview Problems",
            "Mastery Mode",
            "Bit Manipulation 2",
            "Recursion 1",
            "Recursion 2",
            "Backtracking",
        ],
    ),
    (
        "Advanced DSA 2",
        "Cover OOP, hashing, sorting, searching, and two-pointer patterns.",
        [
            "OOP 1: Introduction",
            "OOP 2: Constructor, Inheritance & Polymorphism",
            "Hashing 1: Introduction",
            "Hashing 2: Problems",
            "Java Advanced Concepts: Collections",
            "Contest 2: Recursion, Maths & OOP",
            "Sorting 1: Count Sort & Merge Sort",
            "Sorting 2: Quick Sort & Comparator Problems",
            "Searching 1: Binary Search on Array",
            "Searching 2: Binary Search Problems",
            "Searching 3: Binary Search on Answer",
            "Two Pointers",
        ],
    ),
    (
        "Advanced DSA 3",
        "Learn linked structures, stacks, queues, trees, and hashing internals.",
        [
            "Linked List 1: Introduction",
            "Linked List 2: Sorting & Detecting Loops",
            "Contest 3: Hashing, Sorting & Searching Discussion",
            "Linked List 3: Problems & Doubly Linked List",
            "Stacks 1: Implementation & Basic Problems",
            "Stacks 2: Nearest Smaller/Greater Element",
            "Queues: Implementation & Problems",
            "Trees 1: Structure & Traversal",
            "Trees 2: Views & Types",
            "Trees 3: Binary Search Trees",
            "Trees 4: LCA & Morris Inorder Traversal",
            "Trees 5: Problems on Trees",
            "Hashing 3: Internal Implementation & Problems",
        ],
    ),
    (
        "Advanced DSA 4",
        "Finish with heaps, dynamic programming, graphs, and greedy algorithms.",
        [
            "Heaps 1: Introduction",
            "Heaps 2: Problems",
            "DP 1: One Dimensional",
            "Contest 5: Trees, Heaps & Greedy",
            "DP 2: Two Dimensional",
            "DP 3: Knapsack",
            "DP 4: Applications of Knapsack",
            "Graphs 1: Introduction, DFS & Cycle Detection",
            "Graphs 2: BFS & Matrix Problems",
            "Graphs 3: MST (Prim's Algorithm) & Dijkstra's Algorithm",
        ],
    ),
]


def seed_curriculum():
    if Section.query.first():
        return

    for section_position, (name, description, topics) in enumerate(CURRICULUM, start=1):
        section = Section(
            name=name, description=description, position=section_position
        )
        db.session.add(section)
        db.session.flush()
        for topic_position, title in enumerate(topics, start=1):
            db.session.add(
                Topic(
                    title=title,
                    section_id=section.id,
                    position=topic_position,
                )
            )
    db.session.commit()

