# thor/src/utils/artifact_manager.py
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import uuid
import logging

logger = logging.getLogger(__name__)

class ArtifactManager:
    """Manages code artifacts, files, and project assets"""
    
    def __init__(self):
        self.artifacts_dir = Path("thor/artifacts")
        self.artifacts_dir.mkdir(exist_ok=True)
        self.artifacts: Dict[str, Dict[str, Any]] = {}
        self._load_artifacts()
    
    def create_artifact(self, name: str, content: str, artifact_type: str = "text") -> str:
        """Create a new artifact"""
        artifact_id = str(uuid.uuid4())
        
        artifact = {
            "id": artifact_id,
            "name": name,
            "type": artifact_type,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "size": len(content),
            "metadata": {}
        }
        
        self.artifacts[artifact_id] = artifact
        self._save_artifact(artifact_id)
        
        logger.info(f"Artifact created: {name} ({artifact_id})")
        return artifact_id
    
    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Get artifact by ID"""
        return self.artifacts.get(artifact_id)
    
    def update_artifact(self, artifact_id: str, content: str) -> bool:
        """Update artifact content"""
        if artifact_id not in self.artifacts:
            return False
        
        artifact = self.artifacts[artifact_id]
        artifact["content"] = content
        artifact["updated_at"] = datetime.now().isoformat()
        artifact["size"] = len(content)
        
        self._save_artifact(artifact_id)
        logger.info(f"Artifact updated: {artifact_id}")
        return True
    
    def delete_artifact(self, artifact_id: str) -> bool:
        """Delete artifact"""
        if artifact_id not in self.artifacts:
            return False
        
        del self.artifacts[artifact_id]
        
        # Remove file
        artifact_file = self.artifacts_dir / f"{artifact_id}.json"
        if artifact_file.exists():
            artifact_file.unlink()
        
        logger.info(f"Artifact deleted: {artifact_id}")
        return True
    
    def list_artifacts(self, artifact_type: str = None) -> List[Dict[str, Any]]:
        """List all artifacts"""
        artifacts = list(self.artifacts.values())
        
        if artifact_type:
            artifacts = [a for a in artifacts if a["type"] == artifact_type]
        
        return artifacts
    
    def search_artifacts(self, query: str) -> List[Dict[str, Any]]:
        """Search artifacts by name or content"""
        results = []
        
        for artifact in self.artifacts.values():
            if (query.lower() in artifact["name"].lower() or 
                query.lower() in artifact["content"].lower()):
                results.append(artifact)
        
        return results
    
    def export_artifact(self, artifact_id: str, filepath: str) -> bool:
        """Export artifact to file"""
        if artifact_id not in self.artifacts:
            return False
        
        artifact = self.artifacts[artifact_id]
        
        try:
            with open(filepath, 'w') as f:
                f.write(artifact["content"])
            
            logger.info(f"Artifact exported: {artifact_id} -> {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export artifact: {str(e)}")
            return False
    
    def _save_artifact(self, artifact_id: str):
        """Save artifact to file"""
        artifact_file = self.artifacts_dir / f"{artifact_id}.json"
        
        with open(artifact_file, 'w') as f:
            json.dump(self.artifacts[artifact_id], f, indent=2)
    
    def _load_artifacts(self):
        """Load all artifacts from files"""
        for artifact_file in self.artifacts_dir.glob("*.json"):
            try:
                with open(artifact_file, 'r') as f:
                    artifact = json.load(f)
                    self.artifacts[artifact["id"]] = artifact
            except Exception as e:
                logger.error(f"Failed to load artifact {artifact_file}: {str(e)}")