import numpy as np
import json
from datetime import datetime

class FederatedOrchestrator:
    """
    Simulates federated learning orchestration
    Implements FedAvg (Federated Averaging) algorithm
    """
    
    def __init__(self):
        self.global_model_version = 1
        self.global_weights = None
        self.pending_updates = []
        self.min_updates_for_aggregation = 3
        
    def initialize_global_model(self, model_shape=(10,)):
        """Initialize global model with random weights"""
        self.global_weights = np.random.randn(*model_shape) * 0.01
        return self.global_weights
    
    def receive_local_update(self, client_id, local_weights, num_samples):
        """Receive and store local model update from a client"""
        update = {
            'client_id': client_id,
            'weights': local_weights,
            'num_samples': num_samples,
            'timestamp': datetime.utcnow(),
            'version': self.global_model_version
        }
        self.pending_updates.append(update)
        return True
    
    def aggregate_updates(self):
        """
        Perform federated averaging (FedAvg) on pending updates
        Weights updates by number of samples from each client
        """
        if len(self.pending_updates) < self.min_updates_for_aggregation:
            return {
                'success': False,
                'message': f'Need at least {self.min_updates_for_aggregation} updates, have {len(self.pending_updates)}'
            }
        
        total_samples = sum(update['num_samples'] for update in self.pending_updates)
        
        if total_samples == 0:
            return {
                'success': False,
                'message': 'Total samples is zero'
            }
        
        new_weights = np.zeros_like(self.global_weights)
        
        for update in self.pending_updates:
            weight = update['num_samples'] / total_samples
            new_weights += weight * np.array(update['weights'])
        
        self.global_weights = new_weights
        self.global_model_version += 1
        
        aggregated_count = len(self.pending_updates)
        self.pending_updates = []
        
        return {
            'success': True,
            'new_version': self.global_model_version,
            'updates_aggregated': aggregated_count,
            'total_samples': total_samples,
            'message': f'Successfully aggregated {aggregated_count} updates'
        }
    
    def get_global_model(self):
        """Return current global model for clients"""
        if self.global_weights is None:
            self.initialize_global_model()
        
        return {
            'version': self.global_model_version,
            'weights': self.global_weights.tolist(),
            'timestamp': datetime.utcnow().isoformat(),
            'pending_updates': len(self.pending_updates)
        }
    
    def simulate_local_training(self, client_data, epochs=5, learning_rate=0.01):
        """
        Simulate local model training on client device
        Returns updated local weights
        """
        if self.global_weights is None:
            self.initialize_global_model()
        
        local_weights = self.global_weights.copy()
        
        num_samples = len(client_data)
        
        for epoch in range(epochs):
            gradient = np.random.randn(*local_weights.shape) * 0.1
            local_weights = local_weights - learning_rate * gradient
        
        return {
            'local_weights': local_weights.tolist(),
            'num_samples': num_samples,
            'training_loss': np.random.uniform(0.1, 0.5)
        }
    
    def get_stats(self):
        """Return orchestrator statistics"""
        return {
            'global_model_version': self.global_model_version,
            'pending_updates': len(self.pending_updates),
            'min_updates_needed': self.min_updates_for_aggregation,
            'can_aggregate': len(self.pending_updates) >= self.min_updates_for_aggregation
        }

federated_orchestrator = FederatedOrchestrator()
