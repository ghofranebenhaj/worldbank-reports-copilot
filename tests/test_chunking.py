from src.chunking import content_hash, make_chunks


def test_chunks_keep_page_numbers():
    pages = [(1, "a " * 600), (2, "b " * 600)]
    chunks = make_chunks(pages, size=300, overlap=50)
    assert {c["page"] for c in chunks} == {1, 2}
    assert all(len(c["content"]) <= 300 for c in chunks)


def test_hash_is_stable_and_config_specific():
    assert content_hash("hello", "800-100") == content_hash("hello", "800-100")
    assert content_hash("hello", "800-100") != content_hash("hello", "500-50")
