from mcp.server.fastmcp import FastMCP
import requests
from dotenv import load_dotenv
import os

# Initialize FastMCP server
mcp = FastMCP("DictionaryMCP")
load_dotenv()

# Merriam-Webster API setup
API_KEY = os.environ.get("API_KEY")
BASE_URL = os.environ.get("BASE_URL")


def fetch_data(word: str):
    """Fetch raw dictionary data from Merriam-Webster"""
    url = f"{BASE_URL}{word}?key={API_KEY}"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def meaning(word: str) -> list[str]:
    """Return list of definitions for a word"""
    try:
        data = fetch_data(word)
        for entry in data:
            if isinstance(entry, dict) and "shortdef" in entry:
                return entry["shortdef"]
        return ["No definitions found."]
    except Exception as e:
        return [f"Error: {e}"]


@mcp.tool()
def part_of_speech(word: str) -> str:
    """Return the part of speech for a word"""
    try:
        data = fetch_data(word)
        for entry in data:
            if isinstance(entry, dict) and "fl" in entry:
                return entry["fl"]
        return "Not found"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def pronunciations(word: str) -> list[str]:
    """Return list of pronunciation strings (no audio)"""
    try:
        data = fetch_data(word)
        for entry in data:
            if isinstance(entry, dict):
                return list({
                    prs.get("mw")
                    for prs in entry.get("hwi", {}).get("prs", [])
                    if "mw" in prs
                })
        return ["Not found"]
    except Exception as e:
        return [f"Error: {e}"]


@mcp.tool()
def stems(word: str) -> list[str]:
    """Return stem words related to the input"""
    try:
        data = fetch_data(word)
        for entry in data:
            if isinstance(entry, dict):
                return list(set(entry.get("meta", {}).get("stems", [])))
        return []
    except Exception as e:
        return [f"Error: {e}"]


@mcp.tool()
def meanings_of_stems(word: str) -> dict:
    """Return meanings of each stem related to the input word."""
    stem_meanings = {}
    try:
        data = fetch_data(word)
        stems0 = []
        for entry in data:
            if isinstance(entry, dict):
                stems0 = list(set(entry.get("meta", {}).get("stems", [])))
                break

        for stem in stems0:
            try:
                stem_data = fetch_data(stem)
                for entry in stem_data:
                    if isinstance(entry, dict) and "shortdef" in entry:
                        stem_meanings[stem] = entry["shortdef"]
                        break
            except Exception as e:
                stem_meanings[stem] = [f"Could not fetch: {e}"]
        return stem_meanings
    except Exception as e:
        return {"error": f"Failed to fetch stems: {e}"}


@mcp.tool()
def stem_info(
    word: str,
    include_meanings: bool = True,
    include_part_of_speech: bool = True,
    include_pronunciations: bool = True
) -> dict:
    """Return info (meanings, part of speech, pronunciation) for each stem of the input word."""
    result = {}
    try:
        # Fetch original word data to get stems
        data = fetch_data(word)
        stems = []
        for entry in data:
            if isinstance(entry, dict):
                stems = list(set(entry.get("meta", {}).get("stems", [])))
                break

        for stem in stems:
            stem_entry = {}
            try:
                stem_data = fetch_data(stem)
                for s_entry in stem_data:
                    if not isinstance(s_entry, dict):
                        continue

                    if include_meanings and not stem_entry.get("meanings") and "shortdef" in s_entry:
                        stem_entry["meanings"] = s_entry["shortdef"]

                    if include_part_of_speech and not stem_entry.get("part_of_speech") and "fl" in s_entry:
                        stem_entry["part_of_speech"] = s_entry["fl"]

                    if include_pronunciations and not stem_entry.get("pronunciations") and "hwi" in s_entry:
                        stem_entry["pronunciations"] = list({
                            prs.get("mw")
                            for prs in s_entry.get("hwi", {}).get("prs", [])
                            if "mw" in prs
                        })

                    if (
                        (not include_meanings or "meanings" in stem_entry) and
                        (not include_part_of_speech or "part_of_speech" in stem_entry) and
                        (not include_pronunciations or "pronunciations" in stem_entry)
                    ):
                        break

            except Exception as e:
                stem_entry = {"error": f"Failed to fetch: {e}"}

            result[stem] = stem_entry

        return result

    except Exception as e:
        return {"error": f"Failed to process stems for '{word}': {e}"}


@mcp.tool()
def full_info(
        word: str,
        include_meanings: bool = True,
        include_part_of_speech: bool = True,
        include_pronunciations: bool = True,
        include_stems: bool = True,
        include_stem_info: bool = True
) -> dict:
    """Return customizable dictionary info including full info for each stem."""
    result = {"word": word}
    try:
        data = fetch_data(word)
        for entry in data:
            if not isinstance(entry, dict):
                continue

            if include_meanings:
                result["meanings"] = entry.get("shortdef", [])

            if include_part_of_speech:
                result["part_of_speech"] = entry.get("fl", "")

            if include_pronunciations:
                result["pronunciations"] = list({
                    prs.get("mw")
                    for prs in entry.get("hwi", {}).get("prs", [])
                    if "mw" in prs
                })

            stems1 = list(set(entry.get("meta", {}).get("stems", []))) if (include_stems or include_stem_info) else []

            if include_stems:
                result["stems"] = stems1

            if include_stem_info:
                stem_info1 = {}
                for stem in stems1:
                    stem_entry = {"meanings": [], "part_of_speech": "", "pronunciations": []}
                    try:
                        stem_data = fetch_data(stem)
                        for s_entry in stem_data:
                            if not isinstance(s_entry, dict):
                                continue

                            if not stem_entry["meanings"] and "shortdef" in s_entry:
                                stem_entry["meanings"] = s_entry["shortdef"]

                            if not stem_entry["part_of_speech"] and "fl" in s_entry:
                                stem_entry["part_of_speech"] = s_entry["fl"]

                            if not stem_entry["pronunciations"] and "hwi" in s_entry:
                                stem_entry["pronunciations"] = list({
                                    prs.get("mw")
                                    for prs in s_entry.get("hwi", {}).get("prs", [])
                                    if "mw" in prs
                                })

                            if stem_entry["meanings"]:
                                break
                    except Exception as e:
                        stem_entry = {"error": f"Failed to fetch: {e}"}

                    stem_info1[stem] = stem_entry

                result["stem_info"] = stem_info1

            return result

        return {"error": "No valid dictionary entry found"}

    except Exception as e:
        return {"error": f"Request failed: {e}"}


# Run the MCP server
if __name__ == "__main__":
    mcp.run()
