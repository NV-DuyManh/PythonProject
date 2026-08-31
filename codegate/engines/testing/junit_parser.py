import logging
import xml.etree.ElementTree as ET

from codegate.engines.testing.schemas import JUnitMetrics

logger = logging.getLogger(__name__)

class JUnitParser:
    """Parses JUnit XML to extract stable metrics."""
    
    @staticmethod
    def parse(xml_content: str) -> JUnitMetrics:
        metrics = JUnitMetrics()
        
        if not xml_content or not xml_content.strip():
            return metrics
            
        try:
            root = ET.fromstring(xml_content)  # nosec B314
            
            # JUnit formats can vary. Sometimes it's <testsuites>, sometimes <testsuite>
            suites = []
            if root.tag == "testsuites":
                suites = list(root.findall("testsuite"))
            elif root.tag == "testsuite":
                suites = [root]
            
            for suite in suites:
                # Add up properties if they exist
                metrics.tests += int(suite.attrib.get("tests", 0))
                metrics.failures += int(suite.attrib.get("failures", 0))
                metrics.errors += int(suite.attrib.get("errors", 0))
                metrics.skipped += int(suite.attrib.get("skipped", 0))
                
                try:
                    metrics.duration += float(suite.attrib.get("time", 0.0))
                except ValueError:
                    pass
            
            # Recalculate passed correctly. (passed = tests - failures - errors - skipped)
            metrics.passed = max(0, metrics.tests - metrics.failures - metrics.errors - metrics.skipped)
            
        except ET.ParseError as e:
            logger.error(f"Malformed JUnit XML: {str(e)}")
            # Do not crash the analysis pipeline on bad XML
        
        return metrics
