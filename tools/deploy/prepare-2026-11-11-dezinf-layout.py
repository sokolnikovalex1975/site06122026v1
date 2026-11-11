#!/usr/bin/env python3
"""Patch only the approved layout section in a fresh Timeweb source backup."""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "site"))
import tracking_laws


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    work = pathlib.Path(sys.argv[1]).resolve()
    source = work / "backup/dezinfektsiya/index.php"
    original = source.read_bytes()
    text = original.decode("utf-8")
    assert not tracking_laws.check_page(text, counters=True), "Existing page violates tracking rules"
    pattern = r'<section class="s" id="pochemu">.*?</section>'
    sections = re.findall(pattern, text, re.S)
    assert len(sections) == 1, "Expected exactly one target section"
    before = sections[0]
    intro = re.search(r'      <p class="sub" data-fade>(.*?)</p>\n', before, re.S)
    assert intro and intro.group(1).startswith("В"), "Expected original introductory paragraph"
    marker = '      <div class="dzf-why-t">\n'
    assert before.count(marker) == 1
    after = before.replace(intro.group(0), "", 1)
    after = after.replace(marker, marker + "        <p>" + intro.group(1) + "</p>\n", 1)
    preview = (ROOT / "dezinfektsiya/index.html").read_text(encoding="utf-8")
    assert re.findall(pattern, preview, re.S) == [after], "Section differs from approved GitHub preview"
    result = text.replace(before, after, 1)
    assert result.replace(after, before, 1).encode("utf-8") == original
    assert not tracking_laws.check_page(result, counters=True), "Patched page violates tracking rules"
    # All scripts, styles and phone/email links must remain byte-identical and ordered.
    for tag in (r'<script\b.*?</script>', r'<style\b.*?</style>',
                r'<a\b[^>]*href="(?:tel:|mailto:)[^"]*"[^>]*>.*?</a>'):
        assert re.findall(tag, text, re.S) == re.findall(tag, result, re.S), tag
    assert "noindex" not in result
    target = work / "pkg/dezinfektsiya/index.php"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(result.encode("utf-8"))
    metadata = {
        "file": "dezinfektsiya/index.php",
        "before_sha256": sha(original),
        "after_sha256": sha(target.read_bytes()),
        "scope": "Move introductory paragraph into the existing left column only",
        "outside_target_section_unchanged": True,
        "scripts_styles_contacts_unchanged": True,
        "tracking_laws": "passed_before_and_after",
    }
    (work / "checks.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    (work / "MANIFEST.sha256").write_text(metadata["after_sha256"] + "  dezinfektsiya/index.php\n")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
