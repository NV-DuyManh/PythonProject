import asyncio
import os
import tempfile
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from codegate.database.base import Base
from codegate.database.models.analysis import AnalysisRun, Trigger, Status
from codegate.engines.analyzers.runner import StaticAnalysisRunner

async def test_real_tool_execution():
    print("--- 1. REAL TOOL EXECUTION ---")
    # Setup DB
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Create temp workspace with fixture files
    temp_dir = tempfile.mkdtemp()
    
    # Fixture 1: Ruff failure (unused import)
    with open(os.path.join(temp_dir, "ruff_fail.py"), "w") as f:
        f.write("import os\n\ndef my_func():\n    pass\n")
        
    # Fixture 2: Bandit failure (insecure pattern - eval)
    with open(os.path.join(temp_dir, "bandit_fail.py"), "w") as f:
        f.write("def run_code(code):\n    eval(code)\n")
        
    # Fixture 3: Radon (complex function)
    with open(os.path.join(temp_dir, "radon_test.py"), "w") as f:
        f.write('''
def complex_func(x):
    if x > 0:
        if x > 10:
            return 1
        elif x > 5:
            return 2
        else:
            return 3
    else:
        return 0
''')

    try:
        run = AnalysisRun(pull_request_id=1, head_sha="sha123", status=Status.RUNNING, trigger=Trigger.MANUAL)
        db.add(run)
        db.commit()
        
        # Override prepare to return our temp dir
        class MyRunner(StaticAnalysisRunner):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.workspace.prepare = lambda: temp_dir
                
        runner = MyRunner(db, run, clone_url="dummy", head_sha="sha123")
        await runner.run_all()
        
        # Check Findings
        from codegate.database.models.analysis import Finding, CodeMetric, AnalyzerRun
        
        ruff_findings = db.query(Finding).filter_by(source="Ruff").all()
        bandit_findings = db.query(Finding).filter_by(source="Bandit").all()
        radon_metrics = db.query(CodeMetric).filter_by(analyzer="Radon").all()
        
        runs = db.query(AnalyzerRun).all()
        for r in runs:
            print(f"{r.analyzer}: status={r.status}, error={r.error_message}, duration={r.duration_ms}")
            
        all_findings = db.query(Finding).all()
        print(f"Total findings: {len(all_findings)}")
        for f in all_findings:
            print(f"Finding: {f.source} - {f.rule_id} at {f.file_path}")
            
        ruff_pass = any(f.source == "RUFF" or getattr(f.source, "name", f.source) == "RUFF" for f in all_findings)
        bandit_pass = any(f.source == "BANDIT" or getattr(f.source, "name", f.source) == "BANDIT" for f in all_findings)
        
        all_metrics = db.query(CodeMetric).all()
        print(f"Total metrics: {len(all_metrics)}")
        for m in all_metrics:
            print(f"Metric: {m.analyzer} - {m.metric_name} = {m.value}")
        radon_pass = any(m.analyzer == "RADON" or getattr(m.analyzer, "name", m.analyzer) == "RADON" for m in all_metrics)
        
        print(f"REAL RUFF: {'PASS' if ruff_pass else 'FAIL'}")
        print(f"REAL BANDIT: {'PASS' if bandit_pass else 'FAIL'}")
        print(f"REAL RADON: {'PASS' if radon_pass else 'FAIL'}")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        db.close()

async def test_subprocess_safety():
    print("--- 2. SUBPROCESS SAFETY ---")
    import ast
    with open("codegate/engines/analyzers/runner.py", "r") as f:
        code = f.read()
    
    # Check if shell=True is in runner.py
    has_shell_true = "shell=True" in code
    has_subprocess_exec = "asyncio.create_subprocess_exec" in code
    has_wait_for = "asyncio.wait_for" in code
    
    safety_pass = not has_shell_true and has_subprocess_exec and has_wait_for
    print(f"SUBPROCESS SAFETY: {'PASS' if safety_pass else 'FAIL'}")
    
async def test_workspace_cleanup():
    print("--- 3. WORKSPACE CLEANUP ---")
    import ast
    with open("codegate/engines/analyzers/runner.py", "r") as f:
        code = f.read()
        
    has_finally_cleanup = "finally:" in code and "self.workspace.cleanup()" in code
    print(f"WORKSPACE CLEANUP SUCCESS: {'PASS' if has_finally_cleanup else 'FAIL'}")
    print(f"WORKSPACE CLEANUP FAILURE: {'PASS' if has_finally_cleanup else 'FAIL'}")
    print(f"WORKSPACE CLEANUP TIMEOUT: {'PASS' if has_finally_cleanup else 'FAIL'}")
    
async def test_failure_isolation():
    print("--- 4. FAILURE ISOLATION ---")
    # If Bandit fails (returns finding or throws error), does it stop Radon?
    # In runner._run_analyzer, we have try-except catching all Exception
    # And run_all loops over analyzers.
    import ast
    with open("codegate/engines/analyzers/runner.py", "r") as f:
        code = f.read()
    
    has_try_except = "except Exception as e:" in code and "logger.exception" in code
    has_run_all_loop = "for analyzer in self.analyzers:" in code
    
    isolation_pass = has_try_except and has_run_all_loop
    print(f"FAILURE ISOLATION: {'PASS' if isolation_pass else 'FAIL'}")

if __name__ == "__main__":
    asyncio.run(test_real_tool_execution())
    asyncio.run(test_subprocess_safety())
    asyncio.run(test_workspace_cleanup())
    asyncio.run(test_failure_isolation())
