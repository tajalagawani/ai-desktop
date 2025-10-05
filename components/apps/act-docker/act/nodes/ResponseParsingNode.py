"""
ResponseParsingNode - Advanced response parsing and extraction operations.
Processes LLM outputs, extracts structured data, validates responses, and handles formatting.
"""

import json
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import yaml
import asyncio

from .base_node import BaseNode, NodeResult, NodeSchema, NodeParameter, NodeParameterType
from ..utils.validation import NodeValidationError

class ResponseParsingOperation:
    EXTRACT_JSON = "extract_json"
    EXTRACT_XML = "extract_xml"
    EXTRACT_YAML = "extract_yaml"
    EXTRACT_CODE_BLOCKS = "extract_code_blocks"
    EXTRACT_MARKDOWN_SECTIONS = "extract_markdown_sections"
    EXTRACT_KEY_VALUE_PAIRS = "extract_key_value_pairs"
    EXTRACT_LISTS = "extract_lists"
    EXTRACT_TABLES = "extract_tables"
    PARSE_STRUCTURED_DATA = "parse_structured_data"
    VALIDATE_FORMAT = "validate_format"
    CLEAN_RESPONSE = "clean_response"
    EXTRACT_ENTITIES = "extract_entities"
    PARSE_CITATIONS = "parse_citations"
    EXTRACT_NUMBERS = "extract_numbers"
    EXTRACT_DATES = "extract_dates"
    EXTRACT_URLS = "extract_urls"
    EXTRACT_EMAILS = "extract_emails"
    SPLIT_INTO_SECTIONS = "split_into_sections"
    NORMALIZE_TEXT = "normalize_text"
    EXTRACT_SENTIMENT = "extract_sentiment"
    PARSE_FUNCTION_CALLS = "parse_function_calls"
    EXTRACT_REASONING_STEPS = "extract_reasoning_steps"

class ResponseParsingNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.name = "ResponseParsingNode"
        self.description = "Advanced response parsing and extraction operations"
        self.version = "1.0.0"
        self.icon_path = "🔍"

    async def execute(self, operation: str, params: Dict[str, Any]) -> NodeResult:
        try:
            operation_map = {
                ResponseParsingOperation.EXTRACT_JSON: self._extract_json,
                ResponseParsingOperation.EXTRACT_XML: self._extract_xml,
                ResponseParsingOperation.EXTRACT_YAML: self._extract_yaml,
                ResponseParsingOperation.EXTRACT_CODE_BLOCKS: self._extract_code_blocks,
                ResponseParsingOperation.EXTRACT_MARKDOWN_SECTIONS: self._extract_markdown_sections,
                ResponseParsingOperation.EXTRACT_KEY_VALUE_PAIRS: self._extract_key_value_pairs,
                ResponseParsingOperation.EXTRACT_LISTS: self._extract_lists,
                ResponseParsingOperation.EXTRACT_TABLES: self._extract_tables,
                ResponseParsingOperation.PARSE_STRUCTURED_DATA: self._parse_structured_data,
                ResponseParsingOperation.VALIDATE_FORMAT: self._validate_format,
                ResponseParsingOperation.CLEAN_RESPONSE: self._clean_response,
                ResponseParsingOperation.EXTRACT_ENTITIES: self._extract_entities,
                ResponseParsingOperation.PARSE_CITATIONS: self._parse_citations,
                ResponseParsingOperation.EXTRACT_NUMBERS: self._extract_numbers,
                ResponseParsingOperation.EXTRACT_DATES: self._extract_dates,
                ResponseParsingOperation.EXTRACT_URLS: self._extract_urls,
                ResponseParsingOperation.EXTRACT_EMAILS: self._extract_emails,
                ResponseParsingOperation.SPLIT_INTO_SECTIONS: self._split_into_sections,
                ResponseParsingOperation.NORMALIZE_TEXT: self._normalize_text,
                ResponseParsingOperation.EXTRACT_SENTIMENT: self._extract_sentiment,
                ResponseParsingOperation.PARSE_FUNCTION_CALLS: self._parse_function_calls,
                ResponseParsingOperation.EXTRACT_REASONING_STEPS: self._extract_reasoning_steps,
            }

            if operation not in operation_map:
                return self._create_error_result(f"Unknown operation: {operation}")

            self._validate_params(operation, params)
            result = await operation_map[operation](params)
            
            return self._create_success_result(result, f"Response parsing operation '{operation}' completed")
            
        except Exception as e:
            return self._create_error_result(f"Response parsing error: {str(e)}")

    async def _extract_json(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract JSON objects from response text."""
        text = params["text"]
        extract_all = params.get("extract_all", False)
        validate_schema = params.get("validate_schema")
        
        json_objects = []
        
        # Pattern to find JSON objects
        json_patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Simple nested JSON
            r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]',  # JSON arrays
        ]
        
        for pattern in json_patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    json_str = match.group(0)
                    parsed = json.loads(json_str)
                    
                    # Validate against schema if provided
                    if validate_schema:
                        self._validate_json_schema(parsed, validate_schema)
                    
                    json_objects.append({
                        "data": parsed,
                        "raw_text": json_str,
                        "start_pos": match.start(),
                        "end_pos": match.end()
                    })
                    
                    if not extract_all:
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        return {
            "json_objects": json_objects,
            "count": len(json_objects),
            "extraction_method": "regex_pattern_matching"
        }

    async def _extract_xml(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract XML elements from response text."""
        text = params["text"]
        root_element = params.get("root_element")
        extract_attributes = params.get("extract_attributes", True)
        
        xml_data = []
        
        # Find XML blocks
        xml_pattern = r'<([^>]+)>.*?</\1>'
        matches = re.finditer(xml_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                xml_str = match.group(0)
                root = ET.fromstring(xml_str)
                
                # Filter by root element if specified
                if root_element and root.tag != root_element:
                    continue
                
                xml_obj = self._xml_to_dict(root, extract_attributes)
                xml_data.append({
                    "data": xml_obj,
                    "raw_xml": xml_str,
                    "root_tag": root.tag,
                    "start_pos": match.start(),
                    "end_pos": match.end()
                })
                
            except ET.ParseError:
                continue
        
        return {
            "xml_objects": xml_data,
            "count": len(xml_data),
            "extraction_method": "xml_parsing"
        }

    async def _extract_yaml(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract YAML blocks from response text."""
        text = params["text"]
        
        yaml_objects = []
        
        # Find YAML blocks (usually marked with ``` yaml or --- separators)
        yaml_patterns = [
            r'```ya?ml\s*\n(.*?)\n```',
            r'---\s*\n(.*?)\n---',
            r'```\s*\n(.*?)\n```'  # Generic code blocks that might be YAML
        ]
        
        for pattern in yaml_patterns:
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    yaml_str = match.group(1)
                    parsed = yaml.safe_load(yaml_str)
                    
                    if parsed is not None:
                        yaml_objects.append({
                            "data": parsed,
                            "raw_yaml": yaml_str,
                            "start_pos": match.start(),
                            "end_pos": match.end()
                        })
                        
                except yaml.YAMLError:
                    continue
        
        return {
            "yaml_objects": yaml_objects,
            "count": len(yaml_objects),
            "extraction_method": "yaml_parsing"
        }

    async def _extract_code_blocks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract code blocks from response text."""
        text = params["text"]
        language_filter = params.get("language_filter")
        include_inline = params.get("include_inline", False)
        
        code_blocks = []
        
        # Extract fenced code blocks
        fenced_pattern = r'```(?:(\w+))?\s*\n(.*?)\n```'
        matches = re.finditer(fenced_pattern, text, re.DOTALL)
        
        for match in matches:
            language = match.group(1) or "unknown"
            code = match.group(2)
            
            if language_filter and language.lower() != language_filter.lower():
                continue
            
            code_blocks.append({
                "code": code,
                "language": language,
                "type": "fenced",
                "start_pos": match.start(),
                "end_pos": match.end()
            })
        
        # Extract inline code if requested
        if include_inline:
            inline_pattern = r'`([^`]+)`'
            matches = re.finditer(inline_pattern, text)
            
            for match in matches:
                code_blocks.append({
                    "code": match.group(1),
                    "language": "inline",
                    "type": "inline",
                    "start_pos": match.start(),
                    "end_pos": match.end()
                })
        
        return {
            "code_blocks": code_blocks,
            "count": len(code_blocks),
            "languages": list(set(block["language"] for block in code_blocks))
        }

    async def _extract_markdown_sections(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract markdown sections by headers."""
        text = params["text"]
        header_level = params.get("header_level", None)
        include_content = params.get("include_content", True)
        
        sections = []
        
        # Pattern for markdown headers
        header_pattern = r'^(#{1,6})\s+(.+)$'
        lines = text.split('\n')
        
        current_section = None
        current_content = []
        
        for i, line in enumerate(lines):
            match = re.match(header_pattern, line.strip())
            
            if match:
                # Save previous section
                if current_section:
                    sections.append({
                        **current_section,
                        "content": '\n'.join(current_content) if include_content else None
                    })
                
                # Start new section
                level = len(match.group(1))
                title = match.group(2)
                
                if header_level is None or level == header_level:
                    current_section = {
                        "title": title,
                        "level": level,
                        "line_number": i + 1
                    }
                    current_content = []
                else:
                    current_section = None
                    current_content = []
            elif current_section and include_content:
                current_content.append(line)
        
        # Add last section
        if current_section:
            sections.append({
                **current_section,
                "content": '\n'.join(current_content) if include_content else None
            })
        
        return {
            "sections": sections,
            "count": len(sections),
            "extraction_method": "markdown_header_parsing"
        }

    async def _extract_key_value_pairs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key-value pairs from text."""
        text = params["text"]
        separator = params.get("separator", ":")
        multiline = params.get("multiline", False)
        
        pairs = []
        
        if multiline:
            # Pattern for multiline key-value pairs
            pattern = rf'^(.+?){re.escape(separator)}\s*\n((?:(?!^.+?{re.escape(separator)}).+\n?)*)'
            matches = re.finditer(pattern, text, re.MULTILINE)
        else:
            # Pattern for single-line key-value pairs
            pattern = rf'^(.+?){re.escape(separator)}\s*(.+)$'
            matches = re.finditer(pattern, text, re.MULTILINE)
        
        for match in matches:
            key = match.group(1).strip()
            value = match.group(2).strip()
            
            pairs.append({
                "key": key,
                "value": value,
                "line_number": text[:match.start()].count('\n') + 1
            })
        
        return {
            "pairs": pairs,
            "count": len(pairs),
            "dictionary": {pair["key"]: pair["value"] for pair in pairs}
        }

    async def _extract_lists(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract lists from text (bullet points, numbered lists)."""
        text = params["text"]
        list_type = params.get("list_type", "all")  # all, bullet, numbered
        
        lists = []
        
        patterns = {}
        if list_type in ["all", "bullet"]:
            patterns["bullet"] = r'^[\s]*[-*+]\s+(.+)$'
        if list_type in ["all", "numbered"]:
            patterns["numbered"] = r'^[\s]*\d+\.\s+(.+)$'
        
        for pattern_name, pattern in patterns.items():
            current_list = []
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                match = re.match(pattern, line)
                if match:
                    current_list.append({
                        "text": match.group(1),
                        "line_number": i + 1
                    })
                elif current_list:
                    # End of current list
                    if len(current_list) > 0:
                        lists.append({
                            "type": pattern_name,
                            "items": current_list,
                            "count": len(current_list)
                        })
                    current_list = []
            
            # Add last list if exists
            if current_list:
                lists.append({
                    "type": pattern_name,
                    "items": current_list,
                    "count": len(current_list)
                })
        
        return {
            "lists": lists,
            "total_lists": len(lists),
            "total_items": sum(lst["count"] for lst in lists)
        }

    async def _extract_tables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tables from markdown or text format."""
        text = params["text"]
        table_format = params.get("table_format", "markdown")  # markdown, csv, pipe
        
        tables = []
        
        if table_format == "markdown":
            # Extract markdown tables
            table_pattern = r'(\|.+\|\n\|[-\s\|:]+\|\n(?:\|.+\|\n?)*)'
            matches = re.finditer(table_pattern, text, re.MULTILINE)
            
            for match in matches:
                table_text = match.group(1)
                table_data = self._parse_markdown_table(table_text)
                
                if table_data:
                    tables.append({
                        "data": table_data,
                        "format": "markdown",
                        "raw_text": table_text,
                        "start_pos": match.start(),
                        "end_pos": match.end()
                    })
        
        return {
            "tables": tables,
            "count": len(tables),
            "extraction_method": f"{table_format}_table_parsing"
        }

    async def _parse_structured_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse mixed structured data from response."""
        text = params["text"]
        formats = params.get("formats", ["json", "yaml", "xml"])
        
        structured_data = {}
        
        if "json" in formats:
            json_result = await self._extract_json({"text": text, "extract_all": True})
            structured_data["json"] = json_result
        
        if "yaml" in formats:
            yaml_result = await self._extract_yaml({"text": text})
            structured_data["yaml"] = yaml_result
        
        if "xml" in formats:
            xml_result = await self._extract_xml({"text": text})
            structured_data["xml"] = xml_result
        
        return {
            "structured_data": structured_data,
            "total_objects": sum(data.get("count", 0) for data in structured_data.values())
        }

    async def _validate_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response format against expected structure."""
        text = params["text"]
        expected_format = params["expected_format"]  # json, xml, yaml, markdown, etc.
        schema = params.get("schema")
        
        validation_result = {
            "is_valid": False,
            "format": expected_format,
            "errors": [],
            "parsed_data": None
        }
        
        try:
            if expected_format == "json":
                data = json.loads(text)
                if schema:
                    self._validate_json_schema(data, schema)
                validation_result["parsed_data"] = data
                validation_result["is_valid"] = True
                
            elif expected_format == "xml":
                data = ET.fromstring(text)
                validation_result["parsed_data"] = self._xml_to_dict(data)
                validation_result["is_valid"] = True
                
            elif expected_format == "yaml":
                data = yaml.safe_load(text)
                validation_result["parsed_data"] = data
                validation_result["is_valid"] = True
                
        except Exception as e:
            validation_result["errors"].append(str(e))
        
        return validation_result

    async def _clean_response(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize response text."""
        text = params["text"]
        operations = params.get("operations", ["trim", "normalize_whitespace"])
        
        cleaned_text = text
        applied_operations = []
        
        for operation in operations:
            if operation == "trim":
                cleaned_text = cleaned_text.strip()
                applied_operations.append("trim")
                
            elif operation == "normalize_whitespace":
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
                applied_operations.append("normalize_whitespace")
                
            elif operation == "remove_markdown":
                # Remove markdown formatting
                cleaned_text = re.sub(r'\*\*(.+?)\*\*', r'\1', cleaned_text)  # Bold
                cleaned_text = re.sub(r'\*(.+?)\*', r'\1', cleaned_text)      # Italic
                cleaned_text = re.sub(r'`(.+?)`', r'\1', cleaned_text)        # Code
                cleaned_text = re.sub(r'#{1,6}\s+', '', cleaned_text)         # Headers
                applied_operations.append("remove_markdown")
                
            elif operation == "remove_html":
                cleaned_text = re.sub(r'<[^>]+>', '', cleaned_text)
                applied_operations.append("remove_html")
                
            elif operation == "normalize_line_endings":
                cleaned_text = cleaned_text.replace('\r\n', '\n').replace('\r', '\n')
                applied_operations.append("normalize_line_endings")
        
        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "applied_operations": applied_operations,
            "character_reduction": len(text) - len(cleaned_text)
        }

    async def _extract_entities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract named entities from text."""
        text = params["text"]
        entity_types = params.get("entity_types", ["person", "organization", "location", "date"])
        
        entities = {}
        
        # Simple pattern-based entity extraction
        patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'https?://[^\s]+',
            "phone": r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b',
            "date": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b',
            "time": r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b',
            "number": r'\b\d+(?:\.\d+)?\b',
            "currency": r'\$\d+(?:\.\d{2})?|\b\d+(?:\.\d{2})?\s*(?:USD|EUR|GBP)\b'
        }
        
        for entity_type in entity_types:
            if entity_type in patterns:
                matches = re.finditer(patterns[entity_type], text, re.IGNORECASE)
                entities[entity_type] = []
                
                for match in matches:
                    entities[entity_type].append({
                        "text": match.group(0),
                        "start_pos": match.start(),
                        "end_pos": match.end()
                    })
        
        return {
            "entities": entities,
            "total_entities": sum(len(ent_list) for ent_list in entities.values())
        }

    async def _parse_citations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse citations and references from text."""
        text = params["text"]
        citation_format = params.get("citation_format", "auto")  # auto, apa, mla, chicago
        
        citations = []
        
        # Common citation patterns
        patterns = [
            r'\(([A-Za-z]+(?:\s+&\s+[A-Za-z]+)?,\s*\d{4})\)',  # (Author, Year)
            r'\[(\d+)\]',  # [1], [2], etc.
            r'(?:See|see)\s+([A-Za-z]+(?:\s+\w+)*\s+\(\d{4}\))',  # See Author (Year)
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, text)
            for match in matches:
                citations.append({
                    "text": match.group(0),
                    "reference": match.group(1),
                    "type": f"pattern_{i+1}",
                    "start_pos": match.start(),
                    "end_pos": match.end()
                })
        
        return {
            "citations": citations,
            "count": len(citations),
            "unique_references": list(set(cit["reference"] for cit in citations))
        }

    async def _extract_numbers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and classify numbers from text."""
        text = params["text"]
        number_types = params.get("number_types", ["integer", "decimal", "percentage", "currency"])
        
        numbers = {}
        
        patterns = {
            "integer": r'\b\d+\b',
            "decimal": r'\b\d+\.\d+\b',
            "percentage": r'\b\d+(?:\.\d+)?%\b',
            "currency": r'\$\d+(?:\.\d{2})?|\b\d+(?:\.\d{2})?\s*(?:USD|EUR|GBP)\b',
            "scientific": r'\b\d+(?:\.\d+)?[eE][+-]?\d+\b'
        }
        
        for num_type in number_types:
            if num_type in patterns:
                matches = re.finditer(patterns[num_type], text)
                numbers[num_type] = []
                
                for match in matches:
                    numbers[num_type].append({
                        "text": match.group(0),
                        "value": self._parse_number_value(match.group(0), num_type),
                        "start_pos": match.start(),
                        "end_pos": match.end()
                    })
        
        return {
            "numbers": numbers,
            "total_numbers": sum(len(num_list) for num_list in numbers.values())
        }

    async def _extract_dates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and parse dates from text."""
        text = params["text"]
        
        dates = []
        
        date_patterns = [
            (r'\b\d{4}-\d{2}-\d{2}\b', '%Y-%m-%d'),  # ISO format
            (r'\b\d{1,2}/\d{1,2}/\d{4}\b', '%m/%d/%Y'),  # US format
            (r'\b\d{1,2}-\d{1,2}-\d{4}\b', '%m-%d-%Y'),  # US format with dashes
            (r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b', '%B %d, %Y'),  # Month day, year
        ]
        
        for pattern, date_format in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    date_str = match.group(0)
                    parsed_date = datetime.strptime(date_str, date_format)
                    
                    dates.append({
                        "text": date_str,
                        "parsed_date": parsed_date.isoformat(),
                        "format": date_format,
                        "start_pos": match.start(),
                        "end_pos": match.end()
                    })
                except ValueError:
                    continue
        
        return {
            "dates": dates,
            "count": len(dates),
            "date_range": self._get_date_range(dates) if dates else None
        }

    async def _extract_urls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract URLs from text."""
        text = params["text"]
        include_domains = params.get("include_domains", True)
        
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?:[^\s.,;!?)]|(?<![.,;!?)]))'
        matches = re.finditer(url_pattern, text)
        
        urls = []
        domains = set()
        
        for match in matches:
            url = match.group(0)
            urls.append({
                "url": url,
                "start_pos": match.start(),
                "end_pos": match.end()
            })
            
            if include_domains:
                domain_match = re.search(r'https?://([^/]+)', url)
                if domain_match:
                    domains.add(domain_match.group(1))
        
        return {
            "urls": urls,
            "count": len(urls),
            "unique_domains": list(domains) if include_domains else None
        }

    async def _extract_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract email addresses from text."""
        text = params["text"]
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.finditer(email_pattern, text)
        
        emails = []
        domains = set()
        
        for match in matches:
            email = match.group(0)
            emails.append({
                "email": email,
                "start_pos": match.start(),
                "end_pos": match.end()
            })
            
            domain = email.split('@')[1]
            domains.add(domain)
        
        return {
            "emails": emails,
            "count": len(emails),
            "unique_domains": list(domains)
        }

    async def _split_into_sections(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Split text into logical sections."""
        text = params["text"]
        split_method = params.get("split_method", "paragraphs")  # paragraphs, sentences, headers
        max_section_length = params.get("max_section_length", 1000)
        
        sections = []
        
        if split_method == "paragraphs":
            paragraphs = text.split('\n\n')
            for i, para in enumerate(paragraphs):
                if para.strip():
                    sections.append({
                        "content": para.strip(),
                        "type": "paragraph",
                        "index": i,
                        "word_count": len(para.split())
                    })
                    
        elif split_method == "sentences":
            # Simple sentence splitting
            sentences = re.split(r'[.!?]+\s+', text)
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    sections.append({
                        "content": sentence.strip(),
                        "type": "sentence",
                        "index": i,
                        "word_count": len(sentence.split())
                    })
                    
        elif split_method == "headers":
            header_sections = await self._extract_markdown_sections({
                "text": text, 
                "include_content": True
            })
            sections = header_sections["sections"]
        
        # Split long sections if needed
        if max_section_length:
            sections = self._split_long_sections(sections, max_section_length)
        
        return {
            "sections": sections,
            "count": len(sections),
            "total_words": sum(section.get("word_count", 0) for section in sections),
            "split_method": split_method
        }

    async def _normalize_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize text formatting and structure."""
        text = params["text"]
        operations = params.get("operations", ["case", "spacing", "punctuation"])
        
        normalized_text = text
        
        for operation in operations:
            if operation == "case":
                # Normalize case to sentence case
                sentences = re.split(r'([.!?]+\s*)', normalized_text)
                normalized_sentences = []
                for sentence in sentences:
                    if sentence and not re.match(r'[.!?]+\s*', sentence):
                        sentence = sentence.strip()
                        if sentence:
                            sentence = sentence[0].upper() + sentence[1:].lower()
                    normalized_sentences.append(sentence)
                normalized_text = ''.join(normalized_sentences)
                
            elif operation == "spacing":
                # Normalize spacing
                normalized_text = re.sub(r'\s+', ' ', normalized_text)
                normalized_text = re.sub(r'\s*([.!?])\s*', r'\1 ', normalized_text)
                
            elif operation == "punctuation":
                # Fix common punctuation issues
                normalized_text = re.sub(r'\s+([,.!?])', r'\1', normalized_text)
                normalized_text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', normalized_text)
        
        return {
            "original_text": text,
            "normalized_text": normalized_text.strip(),
            "operations_applied": operations
        }

    async def _extract_sentiment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract sentiment indicators from text."""
        text = params["text"]
        
        positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic", 
            "perfect", "love", "like", "enjoy", "happy", "pleased", "satisfied"
        ]
        
        negative_words = [
            "bad", "terrible", "awful", "horrible", "hate", "dislike", "angry",
            "frustrated", "disappointed", "sad", "upset", "annoyed", "poor"
        ]
        
        text_lower = text.lower()
        positive_count = sum(text_lower.count(word) for word in positive_words)
        negative_count = sum(text_lower.count(word) for word in negative_words)
        
        total_words = len(text.split())
        
        sentiment_score = (positive_count - negative_count) / max(total_words, 1)
        
        if sentiment_score > 0.1:
            sentiment = "positive"
        elif sentiment_score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "total_words": total_words
        }

    async def _parse_function_calls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse function calls from LLM responses."""
        text = params["text"]
        
        function_calls = []
        
        # Pattern for function calls in various formats
        patterns = [
            r'(\w+)\((.*?)\)',  # function_name(args)
            r'call\s+(\w+)\s+with\s+(.*)',  # call function_name with args
            r'execute\s+(\w+)\((.*?)\)',  # execute function_name(args)
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                function_name = match.group(1)
                args_str = match.group(2)
                
                # Try to parse arguments
                try:
                    # Simple argument parsing
                    args = self._parse_function_args(args_str)
                    
                    function_calls.append({
                        "function_name": function_name,
                        "arguments": args,
                        "raw_text": match.group(0),
                        "start_pos": match.start(),
                        "end_pos": match.end()
                    })
                except:
                    function_calls.append({
                        "function_name": function_name,
                        "arguments": {"raw": args_str},
                        "raw_text": match.group(0),
                        "start_pos": match.start(),
                        "end_pos": match.end()
                    })
        
        return {
            "function_calls": function_calls,
            "count": len(function_calls),
            "unique_functions": list(set(call["function_name"] for call in function_calls))
        }

    async def _extract_reasoning_steps(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract reasoning steps from LLM responses."""
        text = params["text"]
        
        steps = []
        
        # Look for numbered steps, bullet points, or step indicators
        step_patterns = [
            r'(?:Step|step)\s+(\d+)[:.]?\s*(.+?)(?=(?:Step|step)\s+\d+|$)',
            r'^(\d+)\.?\s+(.+?)(?=^\d+\.|$)',
            r'(?:First|Second|Third|Finally|Next|Then),?\s*(.+?)(?=(?:First|Second|Third|Finally|Next|Then)|$)',
        ]
        
        for pattern in step_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            current_steps = []
            
            for match in matches:
                if len(match.groups()) == 2:
                    step_num = match.group(1)
                    content = match.group(2).strip()
                else:
                    step_num = len(current_steps) + 1
                    content = match.group(1).strip()
                
                current_steps.append({
                    "step_number": step_num,
                    "content": content,
                    "start_pos": match.start(),
                    "end_pos": match.end()
                })
            
            if current_steps:
                steps.extend(current_steps)
                break  # Use first matching pattern
        
        return {
            "reasoning_steps": steps,
            "step_count": len(steps),
            "has_structured_reasoning": len(steps) > 0
        }

    def _xml_to_dict(self, element, include_attributes=True):
        """Convert XML element to dictionary."""
        result = {}
        
        if include_attributes and element.attrib:
            result["@attributes"] = element.attrib
        
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            result["text"] = element.text.strip()
        
        for child in element:
            child_data = self._xml_to_dict(child, include_attributes)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result

    def _parse_markdown_table(self, table_text):
        """Parse markdown table into structured data."""
        lines = table_text.strip().split('\n')
        if len(lines) < 3:
            return None
        
        # Header row
        headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]
        
        # Data rows (skip separator row)
        rows = []
        for line in lines[2:]:
            if line.strip():
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if len(cells) == len(headers):
                    row_dict = {headers[i]: cells[i] for i in range(len(headers))}
                    rows.append(row_dict)
        
        return {
            "headers": headers,
            "rows": rows,
            "row_count": len(rows)
        }

    def _validate_json_schema(self, data, schema):
        """Simple JSON schema validation."""
        # This is a basic implementation - could be extended with jsonschema library
        if "type" in schema:
            expected_type = schema["type"]
            if expected_type == "object" and not isinstance(data, dict):
                raise ValueError(f"Expected object, got {type(data).__name__}")
            elif expected_type == "array" and not isinstance(data, list):
                raise ValueError(f"Expected array, got {type(data).__name__}")

    def _parse_number_value(self, text, number_type):
        """Parse number value based on type."""
        try:
            if number_type == "integer":
                return int(text)
            elif number_type in ["decimal", "currency"]:
                # Remove currency symbols
                clean_text = re.sub(r'[^\d.]', '', text)
                return float(clean_text)
            elif number_type == "percentage":
                return float(text.replace('%', ''))
            elif number_type == "scientific":
                return float(text)
        except:
            return text

    def _get_date_range(self, dates):
        """Get date range from extracted dates."""
        if not dates:
            return None
        
        parsed_dates = [datetime.fromisoformat(d["parsed_date"]) for d in dates]
        return {
            "earliest": min(parsed_dates).isoformat(),
            "latest": max(parsed_dates).isoformat(),
            "span_days": (max(parsed_dates) - min(parsed_dates)).days
        }

    def _split_long_sections(self, sections, max_length):
        """Split sections that exceed maximum length."""
        split_sections = []
        
        for section in sections:
            content = section.get("content", "")
            if len(content) <= max_length:
                split_sections.append(section)
            else:
                # Split into chunks
                words = content.split()
                current_chunk = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + 1 > max_length and current_chunk:
                        # Start new chunk
                        split_sections.append({
                            **section,
                            "content": " ".join(current_chunk),
                            "is_split": True,
                            "original_index": section.get("index")
                        })
                        current_chunk = [word]
                        current_length = len(word)
                    else:
                        current_chunk.append(word)
                        current_length += len(word) + 1
                
                # Add remaining chunk
                if current_chunk:
                    split_sections.append({
                        **section,
                        "content": " ".join(current_chunk),
                        "is_split": True,
                        "original_index": section.get("index")
                    })
        
        return split_sections

    def _parse_function_args(self, args_str):
        """Parse function arguments string."""
        try:
            # Try to parse as JSON
            return json.loads(f"[{args_str}]")
        except:
            # Fall back to simple comma splitting
            args = [arg.strip().strip('"\'') for arg in args_str.split(',')]
            return args

    def _validate_params(self, operation: str, params: Dict[str, Any]) -> None:
        """Validate operation parameters."""
        required_params = {
            ResponseParsingOperation.EXTRACT_JSON: ["text"],
            ResponseParsingOperation.EXTRACT_XML: ["text"],
            ResponseParsingOperation.EXTRACT_YAML: ["text"],
            ResponseParsingOperation.EXTRACT_CODE_BLOCKS: ["text"],
            ResponseParsingOperation.EXTRACT_MARKDOWN_SECTIONS: ["text"],
            ResponseParsingOperation.EXTRACT_KEY_VALUE_PAIRS: ["text"],
            ResponseParsingOperation.EXTRACT_LISTS: ["text"],
            ResponseParsingOperation.EXTRACT_TABLES: ["text"],
            ResponseParsingOperation.PARSE_STRUCTURED_DATA: ["text"],
            ResponseParsingOperation.VALIDATE_FORMAT: ["text", "expected_format"],
            ResponseParsingOperation.CLEAN_RESPONSE: ["text"],
            ResponseParsingOperation.EXTRACT_ENTITIES: ["text"],
            ResponseParsingOperation.PARSE_CITATIONS: ["text"],
            ResponseParsingOperation.EXTRACT_NUMBERS: ["text"],
            ResponseParsingOperation.EXTRACT_DATES: ["text"],
            ResponseParsingOperation.EXTRACT_URLS: ["text"],
            ResponseParsingOperation.EXTRACT_EMAILS: ["text"],
            ResponseParsingOperation.SPLIT_INTO_SECTIONS: ["text"],
            ResponseParsingOperation.NORMALIZE_TEXT: ["text"],
            ResponseParsingOperation.EXTRACT_SENTIMENT: ["text"],
            ResponseParsingOperation.PARSE_FUNCTION_CALLS: ["text"],
            ResponseParsingOperation.EXTRACT_REASONING_STEPS: ["text"],
        }

        if operation in required_params:
            for param in required_params[operation]:
                if param not in params:
                    raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            name="ResponseParsingNode",
            description="Advanced response parsing and extraction operations",
            version="1.0.0",
            icon_path="🔍",
            auth_params=[],
            parameters=[
                NodeParameter(
                    name="text",
                    param_type=NodeParameterType.STRING,
                    required=True,
                    description="Text content to parse and extract from"
                ),
                NodeParameter(
                    name="extract_all",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Extract all occurrences (for JSON/XML/YAML extraction)"
                ),
                NodeParameter(
                    name="validate_schema",
                    param_type=NodeParameterType.OBJECT,
                    required=False,
                    description="JSON schema to validate extracted data against"
                ),
                NodeParameter(
                    name="language_filter",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Filter code blocks by programming language"
                ),
                NodeParameter(
                    name="include_inline",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Include inline code blocks in extraction"
                ),
                NodeParameter(
                    name="header_level",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Specific header level to extract (1-6)"
                ),
                NodeParameter(
                    name="separator",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Key-value separator character (default: :)"
                ),
                NodeParameter(
                    name="list_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Type of lists to extract: all, bullet, numbered"
                ),
                NodeParameter(
                    name="table_format",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Table format to parse: markdown, csv, pipe"
                ),
                NodeParameter(
                    name="formats",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Data formats to extract: json, yaml, xml"
                ),
                NodeParameter(
                    name="expected_format",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Expected response format for validation"
                ),
                NodeParameter(
                    name="operations",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Text cleaning operations to apply"
                ),
                NodeParameter(
                    name="entity_types",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Types of entities to extract"
                ),
                NodeParameter(
                    name="number_types",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Types of numbers to extract"
                ),
                NodeParameter(
                    name="split_method",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Method for splitting text: paragraphs, sentences, headers"
                ),
                NodeParameter(
                    name="max_section_length",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Maximum length for text sections"
                )
            ]
        )