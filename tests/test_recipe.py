from ruamel.yaml import round_trip_dump

from souschef.recipe import Recipe


def test_load_pure_yaml_recipe(path_data):
    recipe = Recipe(load_file=path_data / "pure.yaml")
    assert recipe["test"].selector == "inline test selector"
    recipe.test.requires.selector = "TESTING SELECTOR"
    assert recipe.test.requires.selector == "TESTING SELECTOR"
    assert recipe.version == 3
    recipe.version.value = 4
    assert recipe["version"] == 4
    recipe["version"] = 5
    assert recipe["version"] == 5
    assert recipe.version == 5
    assert recipe.package.name == "foo"
    assert recipe.package.version == "1.0.0"
    assert recipe.test.requires == ["pip", "pytest"]
    assert len(recipe.test.requires) == 2
    assert "pip" in recipe.test.requires
    assert recipe.test.commands == ["pytest foo"]
    assert recipe.key_extra == ["bar"]


def test_create_selector(path_data, tmpdir):
    selector_folder = tmpdir.mkdir("selector-output")
    recipe = Recipe(load_file=path_data / "without_selector.yaml")
    assert recipe["foo_section"].selector == ""
    assert recipe["foo_section"]["bar_section"].selector == ""
    assert recipe["foo_section"]["bar_section"] == ["val1", "val2"]
    assert recipe["foo_section"]["bar_section"][0].selector == ""
    recipe["foo_section"]["bar_section"][0].selector = "win"
    assert recipe["foo_section"]["bar_section"][0].selector == "win"
    recipe["foo_section"]["bar_section"][0].selector = "osx"
    assert recipe["foo_section"]["bar_section"][0].selector == "osx"
    assert recipe["foo_bar"] == 1
    recipe["foo_bar"].value = 2
    assert recipe["foo_bar"] == 2
    assert recipe["foo_bar"] == 2
    recipe["foo_bar"] = 3
    assert recipe["foo_bar"] == 3

    recipe["foo_section"].selector = "FOO SELECTOR"
    with open(selector_folder / "output_selector.yaml", "w") as f:
        round_trip_dump(recipe._yaml, f)

    with open(selector_folder / "output_selector.yaml", "r") as f:
        content = f.readlines()
    assert content == [
        "foo_section:  # [FOO SELECTOR]\n",
        "  bar_section:\n",
        "  - val1  # [osx]\n",
        "  - val2\n",
        "foo_bar: 3\n",
    ]


def test_get_set_constrain(path_data, tmpdir):
    recipe = Recipe(load_file=path_data / "constrains.yaml")
    assert recipe.requirements.host == ["python >=3.6,<3.9", "pip >20.0.0", "pytest"]
    recipe.requirements.host[0] = "python"
    recipe.requirements.host[1] = "pip"
    recipe.requirements.host[2] = "pytest <=5.0.1"

    assert recipe.requirements.host == ["python", "pip", "pytest <=5.0.1"]

    constrain_folder = tmpdir.mkdir("constrain-output")
    with open(constrain_folder / "output_constrain.yaml", "w") as f:
        round_trip_dump(recipe._yaml, f)

    with open(constrain_folder / "output_constrain.yaml", "r") as f:
        content = f.read()
    assert (
        content
        == """requirements:
  host:
  - python
  - pip
  - pytest <=5.0.1
"""
    )


def test_inline_comment(path_data, tmpdir):
    recipe = Recipe(load_file=path_data / "without_selector.yaml")
    assert recipe.foo_section.inline_comment == ""
    assert recipe["foo_section"].inline_comment == ""

    recipe["foo_section"].inline_comment = "FOO INLINE COMMENT"
    assert recipe["foo_section"].inline_comment == "# FOO INLINE COMMENT"
    recipe.foo_section.inline_comment = "FOO COMMENT 2"
    assert recipe["foo_section"].inline_comment == "# FOO COMMENT 2"

    assert recipe["foo_section"]["bar_section"][0].inline_comment == ""
    recipe["foo_section"]["bar_section"][0].inline_comment = "INLINE VAL1"
    assert recipe["foo_section"]["bar_section"][0].inline_comment == "# INLINE VAL1"

    output_folder = tmpdir.mkdir("inline-comment-output")
    with open(output_folder / "output_constrain.yaml", "w") as f:
        round_trip_dump(recipe._yaml, f)

    with open(output_folder / "output_constrain.yaml", "r") as f:
        content = f.read()
    assert (
        content
        == """foo_section: # FOO COMMENT 2
  bar_section:
  - val1 # INLINE VAL1
  - val2
foo_bar: 1
"""
    )