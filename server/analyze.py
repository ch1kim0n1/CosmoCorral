import json
import os
from pathlib import Path
from typing import List, Dict, Any
import google.generativeai as genai
from datetime import datetime


class GeminiAnomalyDetector:
    """Detect anomalies in timeslot data using Gemini API."""
    
    def __init__(self, api_key: str = None):
        """Initialize with Gemini API key."""
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def load_timeslot_data(self, data_dir: str) -> List[Dict[str, Any]]:
        """Load all cleaned timeslot JSON files."""
        timeslot_dir = Path(data_dir) / "timeslots"
        
        if not timeslot_dir.exists():
            raise FileNotFoundError(f"Timeslots directory not found: {timeslot_dir}")
        
        timeslots = []
        for file_path in sorted(timeslot_dir.glob("*.json")):
            with open(file_path, 'r') as f:
                data = json.load(f)
                data['_source_file'] = file_path.name
                timeslots.append(data)
        
        return timeslots
    
    def prepare_prompt(self, timeslots: List[Dict[str, Any]]) -> str:
        """Prepare analysis prompt for Gemini."""
        prompt = """You are an expert data analyst specializing in behavioral and system anomaly detection.

Analyze the following timeslot data and identify anomalies. Focus on:

1. **System Performance Anomalies**: Unusual CPU, memory, disk usage patterns
2. **User Behavior Anomalies**: Abnormal focus levels, typing speed, mouse behavior
3. **Emotional/Sentiment Anomalies**: Negative emotions, low confidence, poor posture
4. **Network Anomalies**: High latency, packet loss, unusual bandwidth
5. **Workflow Anomalies**: Excessive context switching, high friction, idle time
6. **Input Pattern Anomalies**: Unusual keyboard/mouse activity

For each anomaly detected, provide:
- Type of anomaly
- Affected timeslot (use timestamp)
- Specific metric(s) involved
- Severity (low/medium/high)
- Brief explanation

Provide output as a JSON array with this structure:
{
  "anomalies": [
    {
      "timestamp": "ISO timestamp",
      "type": "anomaly_type",
      "severity": "low|medium|high",
      "metrics": ["metric1", "metric2"],
      "values": {"metric1": value1, "metric2": value2},
      "explanation": "Brief description"
    }
  ],
  "summary": {
    "total_anomalies": 0,
    "by_severity": {"low": 0, "medium": 0, "high": 0},
    "by_type": {}
  }
}

Timeslot Data:
"""
        
        # Format timeslots for analysis
        formatted_data = []
        for ts in timeslots:
            # Extract key metrics from nested structure
            metadata = ts.get('metadata', {})
            data = ts.get('data', {})
            
            summary = {
                'timestamp': metadata.get('timestamp'),
                'session_id': metadata.get('session_id'),
                'system': data.get('system_metrics', {}),
                'focus': data.get('focus_metrics', {}),
                'camera': data.get('camera_data', {}),
                'voice': data.get('voice_data', {}),
                'input': data.get('input_metrics', {}),
                'mouse': data.get('mouse_dynamics', {}),
                'screen': data.get('screen_interactions', {}),
                'network': data.get('network_metrics', {}),
                'file': data.get('file_metadata', {})
            }
            formatted_data.append(summary)
        
        prompt += json.dumps(formatted_data, indent=2)
        return prompt
    
    def analyze_with_gemini(self, timeslots: List[Dict[str, Any]], mode: str = "batch") -> Dict[str, Any]:
        """Send data to Gemini for anomaly detection.
        
        Args:
            timeslots: List of timeslot data to analyze
            mode: "batch" for historical analysis, "realtime" for single timeslot
        """
        if not self.model:
            raise ValueError(
                "Gemini API key not configured. "
                "Set GEMINI_API_KEY environment variable or pass api_key to constructor."
            )
        
        if mode == "realtime" and len(timeslots) == 1:
            print(f"Analyzing single timeslot in real-time mode...")
        else:
            print(f"Analyzing {len(timeslots)} timeslots with Gemini...")
        
        prompt = self.prepare_prompt(timeslots)
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])  # Remove first and last lines
                if response_text.startswith('json'):
                    response_text = response_text[4:].strip()
            
            result = json.loads(response_text)
            return result
            
        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Response text: {response.text[:500]}...")
            raise
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise
    
    def analyze_realtime(self, timeslot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single timeslot in real-time.
        
        Args:
            timeslot_data: Single timeslot data dict
            
        Returns:
            Anomaly detection results for the single timeslot
        """
        return self.analyze_with_gemini([timeslot_data], mode="realtime")
    
    def save_results(self, results: Dict[str, Any], output_dir: str):
        """Save anomaly detection results."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Save full results
        results_file = output_path / f"gemini_anomalies_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'analysis_timestamp': datetime.now().isoformat(),
                'model': 'gemini-pro',
                'results': results
            }, f, indent=2)
        
        # Save human-readable report
        report_file = output_path / f"anomaly_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("GEMINI ANOMALY DETECTION REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: Gemini Pro\n\n")
            
            summary = results.get('summary', {})
            f.write(f"Total Anomalies Detected: {summary.get('total_anomalies', 0)}\n\n")
            
            # Severity breakdown
            by_severity = summary.get('by_severity', {})
            f.write("By Severity:\n")
            for severity, count in by_severity.items():
                f.write(f"  {severity.upper()}: {count}\n")
            
            # Type breakdown
            f.write("\nBy Type:\n")
            by_type = summary.get('by_type', {})
            for atype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {atype}: {count}\n")
            
            # Detailed anomalies
            f.write("\n" + "=" * 70 + "\n")
            f.write("DETAILED ANOMALIES\n")
            f.write("=" * 70 + "\n\n")
            
            for i, anomaly in enumerate(results.get('anomalies', []), 1):
                f.write(f"{i}. [{anomaly.get('severity', 'unknown').upper()}] {anomaly.get('type', 'unknown')}\n")
                f.write(f"   Timestamp: {anomaly.get('timestamp', 'unknown')}\n")
                f.write(f"   Metrics: {', '.join(anomaly.get('metrics', []))}\n")
                f.write(f"   Values: {json.dumps(anomaly.get('values', {}))}\n")
                f.write(f"   Explanation: {anomaly.get('explanation', 'N/A')}\n\n")
            
            f.write("=" * 70 + "\n")
        
        return results_file, report_file


def analyze(data_dir: str = None, output_dir: str = None, api_key: str = None, mode: str = "batch"):
    """Main analysis function for batch or real-time anomaly detection.
    
    Args:
        data_dir: Path to data directory
        output_dir: Path to save results
        api_key: Gemini API key (optional if set in environment)
        mode: "batch" for historical analysis, "realtime" for continuous monitoring
    """
    # Set default paths
    if data_dir is None:
        data_dir = r"C:\rowdyhack-25\client\eyecore_mvp\data"
    
    if output_dir is None:
        output_dir = r"C:\rowdyhack-25\server\analysis_results"
    
    # Get API key from environment if not provided
    if api_key is None:
        api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("ERROR: Gemini API key not found.")
        print("Please set GEMINI_API_KEY environment variable or pass api_key parameter.")
        print("\nExample usage:")
        print("  analyze(api_key='your-api-key-here')")
        return None
    
    # Initialize detector
    detector = GeminiAnomalyDetector(api_key=api_key)
    
    # Load data
    print(f"Loading timeslot data from: {data_dir}")
    timeslots = detector.load_timeslot_data(data_dir)
    print(f"Loaded {len(timeslots)} timeslots\n")
    
    # Analyze with Gemini
    results = detector.analyze_with_gemini(timeslots, mode=mode)
    
    # Save results
    print(f"\nSaving results to: {output_dir}")
    results_file, report_file = detector.save_results(results, output_dir)
    
    print("\nAnalysis complete!")
    print(f"  Results: {results_file}")
    print(f"  Report: {report_file}")
    
    # Print summary
    summary = results.get('summary', {})
    print(f"\nSummary: {summary.get('total_anomalies', 0)} anomalies detected")
    
    return results


def analyze_stream(api_key: str = None, callback=None):
    """Monitor and analyze timeslots in real-time as they arrive.
    
    Args:
        api_key: Gemini API key
        callback: Optional function to call with results: callback(anomalies)
    """
    if api_key is None:
        api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("ERROR: Gemini API key not found.")
        return None
    
    detector = GeminiAnomalyDetector(api_key=api_key)
    data_dir = Path(r"C:\rowdyhack-25\client\eyecore_mvp\data\timeslots")
    
    print("Real-time anomaly detection active...")
    print(f"Monitoring: {data_dir}")
    print("Press Ctrl+C to stop\n")
    
    processed_files = set()
    
    try:
        import time
        while True:
            # Check for new timeslot files
            current_files = set(data_dir.glob("*.json"))
            new_files = current_files - processed_files
            
            for file_path in sorted(new_files):
                try:
                    print(f"New timeslot detected: {file_path.name}")
                    
                    # Load and analyze
                    with open(file_path, 'r') as f:
                        timeslot = json.load(f)
                    
                    results = detector.analyze_realtime(timeslot)
                    
                    # Handle results
                    anomalies = results.get('anomalies', [])
                    if anomalies:
                        print(f"  ⚠️  {len(anomalies)} anomalies detected!")
                        for anomaly in anomalies:
                            print(f"    - [{anomaly.get('severity', '?').upper()}] {anomaly.get('type')}")
                    else:
                        print("  ✓ No anomalies detected")
                    
                    # Call callback if provided
                    if callback:
                        callback(results)
                    
                    processed_files.add(file_path)
                    
                except Exception as e:
                    print(f"  Error processing {file_path.name}: {e}")
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\nReal-time monitoring stopped.")
        print(f"Processed {len(processed_files)} timeslots.")


if __name__ == "__main__":
    # Run analysis
    # Set your API key via environment variable: set GEMINI_API_KEY=your-key-here
    # Or pass it directly: analyze(api_key='your-key-here')
    analyze()
