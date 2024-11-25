from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    """
    Generates bot responses based on the user's message and session data.
    """
    bot_responses = []

    # Retrieve the current question index from the session
    current_question_index = session.get("current_question_index")

    # If no current question index, start the quiz
    if current_question_index is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)

        # Start with the first question
        session["current_question_index"] = 0
        session["answers"] = {}
        next_question = get_question_text_with_options(0)
        bot_responses.append(next_question)
        session.save()
        return bot_responses

    # Record the user's answer for the current question
    success, error = record_current_answer(message, current_question_index, session)
    if not success:
        return [error]  # If validation failed, return the error message

    # Move to the next question or generate the final response
    current_question_index += 1
    if current_question_index < len(PYTHON_QUESTION_LIST):
        next_question = get_question_text_with_options(current_question_index)
        bot_responses.append(next_question)
        session["current_question_index"] = current_question_index
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)
        session.pop("current_question_index")  # Clear session data
        session.pop("answers")
    
    session.save()
    return bot_responses


def record_current_answer(answer, current_question_index, session):
    """
    Validates and stores the user's answer for the current question in the session.
    """
    if current_question_index >= len(PYTHON_QUESTION_LIST):
        return False, "Invalid question or session expired. Please restart the quiz."

    # Get the correct answer for the current question
    correct_answer = PYTHON_QUESTION_LIST[current_question_index]["answer"]

    # Store the user's answer and correctness in the session
    session["answers"][current_question_index] = {
        "user_answer": answer.strip(),
        "is_correct": answer.strip().lower() == correct_answer.strip().lower()
    }
    session.save()

    return True, ""


def get_question_text_with_options(question_index):
    """
    Retrieves the question text along with its options for the given question index.
    """
    question_data = PYTHON_QUESTION_LIST[question_index]
    question_text = question_data["question_text"]
    options = question_data["options"]

    # Format the question with its options
    formatted_question = f"{question_text}\n"
    for i, option in enumerate(options, start=1):
        formatted_question += f"{i}. {option}\n"

    return formatted_question.strip()


def generate_final_response(session):
    """
    Generates the final response message with the user's score.
    """
    answers = session.get("answers", {})
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = sum(1 for answer in answers.values() if answer["is_correct"])

    # Create the final message
    return (
        f"Quiz complete! You answered {correct_answers} out of {total_questions} "
        f"questions correctly. Thank you for participating!"
    )
