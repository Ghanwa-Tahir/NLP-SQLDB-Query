def annotate_column_purpose(column_name):
    name = column_name.lower()
    if "type" in name or "category" in name:
        return "classification"
    elif "name" in name or "title" in name:
        return "label"
    elif "id" in name:
        return "identifier"
    elif "location" in name or "city" in name or "region" in name:
        return "location"
    elif "date" in name or "time" in name:
        return "timestamp"
    else:
        return "unknown"
