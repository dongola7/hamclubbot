# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

import sqlite3
from hamclubbot.extensions.util.persistentstore import PersistentGuildStore

def test_create_db(tmp_path):
    db_path = tmp_path / "test.db"
    store = PersistentGuildStore(123, db_path)

    with sqlite3.connect(db_path) as conn:
        user_version = conn.execute("PRAGMA USER_VERSION").fetchone()[0]
        assert user_version == 1, "USER_VERSION should be 1"

        table_name = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='storage'").fetchone()
        assert table_name is not None, "'storage' table should exist"

def test_get_set_delete_values(tmp_path):
    store = PersistentGuildStore(123, tmp_path / "test.db")

    assert store.get_value('abc') is None, "return None if key does not exist"
    assert store.get_value('abc', default = 'default_value') == "default_value", "return default if key does not exist"

    store.set_value('abc', 'stored_value')
    assert store.get_value('abc') == "stored_value", "return stored value for existing key"

    store.delete_value('abc')
    assert store.get_value('abc') is None, "key should be deleted"

def test_get_keys(tmp_path):
    store = PersistentGuildStore(123, tmp_path / "test.db")

    store.set_value('a_key', 'value1')
    store.set_value('b_key', 'value2')
    store.set_value('another_key', 'value3')

    assert store.get_keys() == ['a_key', 'another_key', 'b_key'], "all keys are returned with no prefix"

    assert store.get_keys('a') == ['a_key', 'another_key'], "only return keys matching prefix"

def test_same_key_multiple_guilds(tmp_path):
    db_path = tmp_path / "test.db"
    store_a = PersistentGuildStore(123, db_path)
    store_b = PersistentGuildStore(456, db_path)

    store_a.set_value('abc', 'store_a_value')
    store_b.set_value('abc', 'store_b_value')

    assert store_a.get_value('abc') == 'store_a_value' and store_b.get_value('abc') == 'store_b_value', "keys are segregated by guild"

def test_get_keys_multiple_guilds(tmp_path):
    db_path = tmp_path / "test.db"
    store_a = PersistentGuildStore(123, db_path)
    store_b = PersistentGuildStore(456, db_path)

    store_a.set_value('abc', 'store_a_abc')
    store_a.set_value('store_a_key', 'store_a_value')
    store_b.set_value('abc', 'store_b_abc')
    store_b.set_value('store_b_key', 'store_b_value')

    assert store_a.get_keys() == ['abc', 'store_a_key'] and store_b.get_keys() == ['abc', 'store_b_key'], "keys are segregated by guild"
    assert store_a.get_keys('store') == ['store_a_key'] and store_b.get_keys('store') == ['store_b_key'], "prefixed keys are segregated by guild"
