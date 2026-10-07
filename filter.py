from config import categories


def calculate_score(title, summary):
    title = title.lower()
    summary = summary.lower()

    score = 0

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in title:
                score += 2

            if keyword in summary:
                score += 1

    return score


def get_tags(title, summary):
    text = (title + " " + summary).lower()

    tags = []

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text:
                tags.append(category)
                break

    return tags