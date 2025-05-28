import base64
import fastavro
import io

# Avro schema (must be shared across encode/decode)
SCHEMA = {
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "age", "type": "int"},
        {"name": "email", "type": ["null", "string"], "default": None},
    ],
}


def encode_record_to_urlsafe(record: dict, schema: dict) -> str:
    """Serialize record to raw Avro bytes and encode to URL-safe base64 string (no padding)."""
    buffer = io.BytesIO()
    fastavro.schemaless_writer(buffer, schema, record)
    raw_bytes = buffer.getvalue()

    encoded = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
    return encoded.rstrip("=")  # remove padding


def decode_urlsafe_to_record(encoded_str: str, schema: dict) -> dict:
    """Decode URL-safe base64 string (restore padding), then deserialize Avro."""
    padding_needed = (-len(encoded_str)) % 4
    padded_str = encoded_str + ("=" * padding_needed)

    raw_bytes = base64.urlsafe_b64decode(padded_str)
    buffer = io.BytesIO(raw_bytes)

    return fastavro.schemaless_reader(buffer, schema)


def main():
    record = {"name": "Alice", "age": 30, "email": "alice@example.com"}

    print("Original record:", record)

    encoded = encode_record_to_urlsafe(record, SCHEMA)
    print("URL-safe base64 string:", encoded)

    decoded = decode_urlsafe_to_record(encoded, SCHEMA)
    print("Decoded record:", decoded)


if __name__ == "__main__":
    main()
