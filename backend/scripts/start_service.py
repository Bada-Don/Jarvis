#!/usr/bin/env python3
"""
Start Service Script

This script starts the FunctionGemma service with proper initialization
and health checks. It can run in different modes (development, production).

Usage:
    python start_service.py [--mode MODE] [--port PORT] [--host HOST]

Options:
    --mode MODE      Run mode: dev, prod (default: dev)
    --port PORT      Port to listen on (default: 5000)
    --host HOST      Host to bind to (default: 127.0.0.1)
    --no-model       Start without loading model (for testing)
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are available."""
    required_modules = [
        ("flask", "Flask"),
        ("flask_cors", "Flask-CORS"),
        ("flask_socketio", "Flask-SocketIO"),
        ("transformers", "Transformers"),
        ("torch", "PyTorch"),
        ("pyautogui", "PyAutoGUI"),
    ]
    
    missing = []
    for module_name, display_name in required_modules:
        try:
            __import__(module_name)
            logger.info(f"✓ {display_name} available")
        except ImportError:
            logger.error(f"✗ {display_name} not found")
            missing.append(display_name)
    
    if missing:
        logger.error("")
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.error("Install with: python scripts/install_dependencies.py")
        return False
    
    return True


def check_model(model_path: str):
    """Check if model is available."""
    if not os.path.exists(model_path):
        logger.warning(f"⚠ Model not found at: {model_path}")
        logger.warning("Download with: python scripts/download_model.py")
        return False
    
    logger.info(f"✓ Model found at: {model_path}")
    return True


def initialize_service(mode: str, load_model: bool):
    """
    Initialize the FunctionGemma service.
    
    Args:
        mode: Run mode (dev or prod)
        load_model: Whether to load the model on startup
    """
    try:
        # Import service components
        from functiongemma_service import FunctionGemmaPlannerService
        from function_registry import FunctionRegistry
        
        logger.info("Initializing Function Registry...")
        registry = FunctionRegistry()
        
        # Register all functions
        from functions import folder_operations, file_operations
        from functions import keyboard_operations, mouse_operations
        from functions import window_management
        
        # Register folder operations
        registry.register_all_from_module(folder_operations, "folder_operations")
        
        # Register file operations
        registry.register_all_from_module(file_operations, "file_operations")
        
        # Register keyboard operations
        registry.register_all_from_module(keyboard_operations, "keyboard_operations")
        
        # Register mouse operations
        registry.register_all_from_module(mouse_operations, "mouse_operations")
        
        # Register window management
        registry.register_all_from_module(window_management, "window_management")
        
        logger.info(f"✓ Registered {len(registry.get_all_functions())} functions")
        
        # Initialize planner service
        logger.info("Initializing FunctionGemma Planner Service...")
        service = FunctionGemmaPlannerService(
            function_registry=registry,
            lazy_load=not load_model  # Load immediately if requested
        )
        
        if load_model:
            logger.info("Loading model (this may take a few seconds)...")
            service.load_model()
        
        logger.info("✓ Service initialized")
        return service, registry
        
    except Exception as e:
        logger.error(f"✗ Service initialization failed: {e}")
        raise


def start_server(host: str, port: int, mode: str, service, registry):
    """
    Start the Flask server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        mode: Run mode (dev or prod)
        service: FunctionGemma service instance
        registry: Function registry instance
    """
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        from flask_socketio import SocketIO
        
        # Create Flask app
        app = Flask(__name__)
        CORS(app)
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        # Store service and registry in app context
        app.config['service'] = service
        app.config['registry'] = registry
        
        # Import monitoring
        from monitoring import get_monitoring_dashboard
        dashboard = get_monitoring_dashboard()
        
        # Health check endpoint
        @app.route('/health', methods=['GET'])
        def health():
            return jsonify({
                "status": "healthy",
                "model_loaded": service.is_loaded(),
                "functions_registered": len(registry.get_all_functions())
            })
        
        # Monitoring dashboard data endpoint
        @app.route('/monitoring/dashboard', methods=['GET'])
        def monitoring_dashboard():
            data = dashboard.get_dashboard_data()
            return jsonify(data)
        
        # Monitoring dashboard HTML
        @app.route('/monitoring', methods=['GET'])
        def monitoring_page():
            from flask import send_file
            import os
            dashboard_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'monitoring_dashboard.html'
            )
            return send_file(dashboard_path)
        
        # Export metrics endpoint
        @app.route('/monitoring/export', methods=['GET'])
        def export_metrics():
            import tempfile
            import os
            
            # Create temp file
            fd, path = tempfile.mkstemp(suffix='.json')
            os.close(fd)
            
            # Export metrics
            dashboard.export_metrics(path)
            
            # Send file
            from flask import send_file
            return send_file(path, as_attachment=True, download_name='metrics.json')
        
        # Execute command endpoint
        @app.route('/execute', methods=['POST'])
        def execute():
            data = request.json
            command = data.get('command', '')
            
            if not command:
                return jsonify({"error": "No command provided"}), 400
            
            try:
                result = service.execute_multi_step_task(command)
                return jsonify(result)
            except Exception as e:
                logger.error(f"Execution error: {e}")
                return jsonify({"error": str(e)}), 500
        
        # List functions endpoint
        @app.route('/functions', methods=['GET'])
        def list_functions():
            functions = registry.get_all_functions()
            return jsonify({
                "count": len(functions),
                "functions": [
                    {
                        "name": name,
                        "category": info.get("category", "unknown")
                    }
                    for name, info in functions.items()
                ]
            })
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✓ FunctionGemma Service Started")
        logger.info("=" * 60)
        logger.info(f"Mode: {mode}")
        logger.info(f"Host: {host}")
        logger.info(f"Port: {port}")
        logger.info(f"Model loaded: {service.is_loaded()}")
        logger.info(f"Functions: {len(registry.get_all_functions())}")
        logger.info("")
        logger.info("Endpoints:")
        logger.info(f"  Health: http://{host}:{port}/health")
        logger.info(f"  Execute: http://{host}:{port}/execute")
        logger.info(f"  Functions: http://{host}:{port}/functions")
        logger.info(f"  Monitoring Dashboard: http://{host}:{port}/monitoring")
        logger.info(f"  Monitoring Data: http://{host}:{port}/monitoring/dashboard")
        logger.info(f"  Export Metrics: http://{host}:{port}/monitoring/export")
        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        # Start server
        debug = (mode == "dev")
        socketio.run(app, host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"✗ Server startup failed: {e}")
        raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Start FunctionGemma service"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["dev", "prod"],
        default="dev",
        help="Run mode (default: dev)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to listen on (default: 5000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--no-model",
        action="store_true",
        help="Start without loading model (for testing)"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("FunctionGemma Integration - Service Startup")
    logger.info("=" * 60)
    logger.info("")
    
    # Check dependencies
    logger.info("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    logger.info("")
    
    # Check model (warning only if not found)
    if not args.no_model:
        logger.info("Checking model...")
        model_path = "./local_models/functiongemma-270m-it"
        check_model(model_path)
        logger.info("")
    
    # Initialize service
    try:
        service, registry = initialize_service(args.mode, not args.no_model)
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)
    
    # Start server
    try:
        start_server(args.host, args.port, args.mode, service, registry)
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 60)
        logger.info("Service stopped by user")
        logger.info("=" * 60)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
