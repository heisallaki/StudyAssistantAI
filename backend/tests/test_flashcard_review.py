from app.services.flashcard_review import apply_review_result


def test_first_good_review_moves_new_card_to_learning():
    status, times_reviewed, times_correct, correct_streak = apply_review_result("new", 0, 0, 0, "good")
    assert status == "learning"
    assert times_reviewed == 1
    assert times_correct == 1
    assert correct_streak == 1


def test_second_consecutive_good_review_marks_card_mastered():
    status, times_reviewed, times_correct, correct_streak = apply_review_result("learning", 1, 1, 1, "good")
    assert status == "mastered"
    assert times_reviewed == 2
    assert times_correct == 2
    assert correct_streak == 2


def test_again_review_resets_streak_and_sets_learning():
    status, times_reviewed, times_correct, correct_streak = apply_review_result("new", 0, 0, 0, "again")
    assert status == "learning"
    assert times_reviewed == 1
    assert times_correct == 0
    assert correct_streak == 0


def test_again_review_demotes_a_mastered_card():
    status, times_reviewed, times_correct, correct_streak = apply_review_result("mastered", 4, 4, 3, "again")
    assert status == "learning"
    assert times_reviewed == 5
    assert times_correct == 4
    assert correct_streak == 0


def test_times_reviewed_always_increments_regardless_of_result():
    _, times_reviewed_good, _, _ = apply_review_result("learning", 2, 1, 1, "good")
    _, times_reviewed_again, _, _ = apply_review_result("learning", 2, 1, 1, "again")
    assert times_reviewed_good == 3
    assert times_reviewed_again == 3