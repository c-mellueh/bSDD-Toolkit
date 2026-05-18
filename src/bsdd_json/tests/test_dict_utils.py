from bsdd_json.tests.helpers import make_dictionary
from bsdd_json.utils import dictionary_utils as dict_utils


class TestSlugify:
    """Test the Method "slugify" to check if it slugifies codes correctly so they can be used in URIs."""

    def test_basic_ascii(self) -> None:
        assert dict_utils.slugify("Hello World") == "Hello-World"

    def test_lowercase_flag(self) -> None:
        assert dict_utils.slugify("Hello World", lowercase=True) == "hello-world"

    def test_german_umlaut_oe(self) -> None:
        assert dict_utils.slugify("Größe", lowercase=True) == "groesse"

    def test_german_umlaut_ae(self) -> None:
        assert dict_utils.slugify("ähnlich", lowercase=True) == "aehnlich"

    def test_german_umlaut_ue(self) -> None:
        assert dict_utils.slugify("überall", lowercase=True) == "ueberall"

    def test_german_sharp_s(self) -> None:
        assert dict_utils.slugify("Straße", lowercase=True) == "strasse"

    def test_german_capital_umlauts(self) -> None:
        result = dict_utils.slugify("Äpfel Öl Über")
        assert "Ae" in result
        assert "Oe" in result
        assert "Ue" in result

    def test_custom_delimiter(self) -> None:
        assert dict_utils.slugify("Hello World", delimiter="_") == "Hello_World"

    def test_strips_leading_trailing_delimiter(self) -> None:
        assert dict_utils.slugify(" Hello ") == "Hello"

    def test_collapses_repeated_delimiters(self) -> None:
        assert dict_utils.slugify("a  b  c") == "a-b-c"

    def test_accent_stripping(self) -> None:
        assert dict_utils.slugify("résumé", lowercase=True) == "resume"

    def test_max_length(self) -> None:
        result = dict_utils.slugify("Hello World Test", max_length=5)
        assert len(result) <= 5

    def test_max_length_strips_trailing_delimiter(self) -> None:
        # Truncation must not leave a trailing delimiter
        result = dict_utils.slugify("abc-def", max_length=4)
        assert not result.endswith("-")

    def test_non_string_coerced(self) -> None:
        assert dict_utils.slugify(42) == "42"

    def test_empty_string(self) -> None:
        assert dict_utils.slugify("") == ""

    def test_numbers_preserved(self) -> None:
        assert dict_utils.slugify("item123") == "item123"


# ===========================================================================
# 3. dictionary_utils.is_uri
# ===========================================================================


class TestIsUri:
    def test_https_url_is_uri(self) -> None:
        assert dict_utils.is_uri("https://identifier.buildingsmart.org/uri/tst/test/1.0/class/X")

    def test_http_url_is_uri(self) -> None:
        assert dict_utils.is_uri("http://example.com/something")

    def test_bare_code_is_not_uri(self) -> None:
        assert not dict_utils.is_uri("just-a-code")

    def test_empty_string_is_not_uri(self) -> None:
        assert not dict_utils.is_uri("")

    def test_path_without_scheme_is_not_uri(self) -> None:
        assert not dict_utils.is_uri("/uri/buildingsmart/ifc/4.3/class/Wall")


# ===========================================================================
# 4. dictionary_utils.get_dictionary_path_from_uri
# ===========================================================================


class TestGetDictionaryPathFromUri:
    BASE = "https://identifier.buildingsmart.org/uri/"

    def test_class_uri_extracts_dict_path(self) -> None:
        uri = f"{self.BASE}acca/LCCbyACCA/0.1/class/Lavori"
        result = dict_utils.get_dictionary_path_from_uri(uri)
        assert result == f"{self.BASE}acca/LCCbyACCA/0.1/"

    def test_prop_uri_extracts_dict_path(self) -> None:
        uri = f"{self.BASE}tst/test/1.0/prop/MyProp"
        result = dict_utils.get_dictionary_path_from_uri(uri)
        assert result == f"{self.BASE}tst/test/1.0/"

    def test_returns_empty_for_short_path(self) -> None:
        # Only org/lib without version
        result = dict_utils.get_dictionary_path_from_uri(f"{self.BASE}org/lib/")
        assert result == ""

    def test_returns_empty_for_wrong_prefix(self) -> None:
        result = dict_utils.get_dictionary_path_from_uri("https://example.com/something")
        assert result == ""

    def test_returns_empty_for_empty_string(self) -> None:
        assert dict_utils.get_dictionary_path_from_uri("") == ""


# ===========================================================================
# 5. dictionary_utils.parse_bsdd_url
# ===========================================================================


class TestParseBsddUrl:
    def test_full_class_uri(self) -> None:
        uri = "https://identifier.buildingsmart.org/uri/hw/som/0.2.0/class/Leiter"
        r = dict_utils.parse_bsdd_url(uri)
        assert r["path_segments"] == ["uri", "hw", "som", "0.2.0", "class", "Leiter"]
        assert r["namespace"] == "hw/som"
        assert r["version"] == "0.2.0"
        assert r["resource_type"] == "class"
        assert r["resource_id"] == "Leiter"

    def test_scheme_and_host(self) -> None:
        uri = "https://identifier.buildingsmart.org/uri/hw/som/0.2.0/class/Leiter"
        r = dict_utils.parse_bsdd_url(uri)
        assert r["scheme"] == "https"
        assert r["host"] == "identifier.buildingsmart.org"

    def test_prop_uri(self) -> None:
        uri = "https://identifier.buildingsmart.org/uri/hw/som/0.2.0/prop/MyProp"
        r = dict_utils.parse_bsdd_url(uri)
        assert r["resource_type"] == "prop"
        assert r["resource_id"] == "MyProp"

    def test_returns_dict(self) -> None:
        r = dict_utils.parse_bsdd_url("https://example.com/uri/a/b/1.0/class/C")
        assert isinstance(r, dict)


# ===========================================================================
# 6. dictionary_utils.build_bsdd_url
# ===========================================================================


class TestBuildBsddUrl:
    def test_builds_class_uri(self) -> None:
        data = {
            "namespace": ["hw", "som"],
            "version": "0.2.0",
            "resource_type": "class",
            "resource_id": "Leiter",
        }
        url = dict_utils.build_bsdd_url(data)
        assert url == "https://identifier.buildingsmart.org/uri/hw/som/0.2.0/class/Leiter"

    def test_trailing_slash_added(self) -> None:
        data = {
            "namespace": ["TST", "TEST"],
            "version": "1.0",
            "resource_type": "dictionary",
            "resource_id": "",
        }
        url = dict_utils.build_bsdd_url(data, trailing_slash=True)
        assert url.endswith("/")

    def test_no_trailing_slash_by_default(self) -> None:
        data = {
            "namespace": ["hw", "som"],
            "version": "0.2.0",
            "resource_type": "class",
            "resource_id": "Leiter",
        }
        url = dict_utils.build_bsdd_url(data)
        assert not url.endswith("/")

    def test_namespace_as_string(self) -> None:
        data = {
            "namespace": "hw/som",
            "version": "0.2.0",
            "resource_type": "class",
            "resource_id": "Leiter",
        }
        url = dict_utils.build_bsdd_url(data)
        assert "hw/som" in url

    def test_empty_data_returns_empty(self) -> None:
        assert dict_utils.build_bsdd_url({}) == ""

    def test_roundtrip(self) -> None:
        uri = "https://identifier.buildingsmart.org/uri/hw/som/0.2.0/class/Leiter"
        parsed = dict_utils.parse_bsdd_url(uri)
        rebuilt = dict_utils.build_bsdd_url(parsed)
        assert rebuilt == uri


# ===========================================================================
# 7. dictionary_utils.is_ifc_reference
# ===========================================================================


class TestDictUtilsIsIfcReference:
    def test_ifc_uri_detected(self) -> None:
        assert dict_utils.is_ifc_reference("https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/Wall")

    def test_non_ifc_uri_not_detected(self) -> None:
        assert not dict_utils.is_ifc_reference("https://identifier.buildingsmart.org/uri/hw/som/0.2.0/class/Leiter")


# ===========================================================================
# 8. dictionary_utils.is_external_ref
# ===========================================================================


class TestDictUtilsIsExternalRef:
    def test_same_dictionary_uri_is_not_external(self) -> None:
        d = make_dictionary()
        uri = "https://identifier.buildingsmart.org/uri/TST/TEST/1.0/class/X"
        assert not dict_utils.is_external_ref(uri, d)

    def test_different_org_is_external(self) -> None:
        d = make_dictionary()
        uri = "https://identifier.buildingsmart.org/uri/OTHER/DICT/1.0/class/X"
        assert dict_utils.is_external_ref(uri, d)

    def test_empty_uri_is_not_external(self) -> None:
        d = make_dictionary()
        assert not dict_utils.is_external_ref("", d)
