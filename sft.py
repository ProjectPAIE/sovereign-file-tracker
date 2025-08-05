#!/usr/bin/env python3
"""
Sovereign File Tracker - Command Line Interface
Main CLI tool for interacting with the SFT system.
"""

import argparse
import sys
import logging
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, Callable
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommandModule:
    """Base class for command modules."""
    
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add command-specific arguments to the parser."""
        pass
    
    def execute(self, args: argparse.Namespace):
        """Execute the command with the given arguments."""
        return self.func(args)


class CommandRouter:
    """Router for discovering and executing command modules."""
    
    def __init__(self):
        self.commands: Dict[str, CommandModule] = {}
        self.commands_dir = Path(__file__).parent / "commands"
    
    def discover_commands(self):
        """Discover command modules from the commands directory."""
        if not self.commands_dir.exists():
            logger.warning(f"Commands directory not found: {self.commands_dir}")
            return
        
        # Import the main commands module
        try:
            commands_module = importlib.import_module("commands")
        except ImportError as e:
            logger.warning(f"Could not import commands module: {e}")
            return
        
        # Discover commands from subdirectories
        for subdir in self.commands_dir.iterdir():
            if subdir.is_dir():
                # First, try to discover from __init__.py
                if (subdir / "__init__.py").exists():
                    self._discover_commands_from_directory(subdir)
                
                # Then, discover from individual Python files in the subdirectory
                for py_file in subdir.glob("*.py"):
                    if py_file.name != "__init__.py":
                        self._discover_commands_from_file(subdir, py_file)
    
    def _discover_commands_from_directory(self, directory: Path):
        """Discover commands from a specific directory."""
        try:
            # Import the directory as a module
            module_name = f"commands.{directory.name}"
            module = importlib.import_module(module_name)
            
            # Look for command functions in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isfunction(obj) and 
                    hasattr(obj, '_is_command') and 
                    obj._is_command):
                    
                    command_name = getattr(obj, '_command_name', name)
                    description = getattr(obj, '_command_description', f'Execute {name}')
                    
                    # Create a command module with the function and its argument parser
                    cmd_module = CommandModule(
                        name=command_name,
                        description=description,
                        func=obj
                    )
                    
                    # Try to get the add_arguments function from the same module
                    if hasattr(module, 'add_arguments'):
                        cmd_module.add_arguments = module.add_arguments
                    
                    self.commands[command_name] = cmd_module
                    # logger.info(f"Discovered command: {command_name}")
        
        except ImportError as e:
            logger.warning(f"Could not import module from {directory}: {e}")
        except Exception as e:
            logger.warning(f"Error discovering commands from {directory}: {e}")
    
    def _discover_commands_from_file(self, directory: Path, py_file: Path):
        """Discover commands from a specific Python file."""
        try:
            # Import the file as a module
            module_name = f"commands.{directory.name}.{py_file.stem}"
            module = importlib.import_module(module_name)
            
            # Look for command functions in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isfunction(obj) and 
                    hasattr(obj, '_is_command') and 
                    obj._is_command):
                    
                    command_name = getattr(obj, '_command_name', name)
                    description = getattr(obj, '_command_description', f'Execute {name}')
                    
                    # Create a command module with the function and its argument parser
                    cmd_module = CommandModule(
                        name=command_name,
                        description=description,
                        func=obj
                    )
                    
                    # Try to get the add_arguments function from the same module
                    if hasattr(module, 'add_arguments'):
                        cmd_module.add_arguments = module.add_arguments
                    
                    self.commands[command_name] = cmd_module
                    # logger.info(f"Discovered command: {command_name}")
        
        except ImportError as e:
            logger.warning(f"Could not import module from {py_file}: {e}")
        except Exception as e:
            logger.warning(f"Error discovering commands from {py_file}: {e}")
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser with discovered commands."""
        parser = argparse.ArgumentParser(
            prog='sft',
            description='Sovereign File Tracker - Command Line Interface',
            epilog='Use "sft <command> --help" for more information about a command.'
        )
        
        # Create subparsers for different commands
        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands',
            metavar='COMMAND'
        )
        
        # Add discovered commands
        for command_name, command_module in self.commands.items():
            subparser = subparsers.add_parser(
                command_name,
                help=command_module.description
            )
            
            # Let the command module add its own arguments
            if hasattr(command_module, 'add_arguments'):
                command_module.add_arguments(subparser)
            
            # Set the default function
            subparser.set_defaults(func=command_module.execute)
        
        return parser
    
    def execute_command(self, args: argparse.Namespace):
        """Execute the specified command."""
        if not args.command:
            return False
        
        if args.command not in self.commands:
            logger.error(f"Unknown command: {args.command}")
            return False
        
        try:
            self.commands[args.command].execute(args)
            return True
        except Exception as e:
            logger.error(f"Error executing command '{args.command}': {e}")
            return False


def command(name: str = None, description: str = None):
    """Decorator to mark functions as commands."""
    def decorator(func):
        func._is_command = True
        func._command_name = name or func.__name__
        func._command_description = description or func.__doc__ or f'Execute {func.__name__}'
        return func
    return decorator


def main():
    """
    Main entry point for the SFT CLI.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Create command router and discover commands
    router = CommandRouter()
    router.discover_commands()
    
    if not router.commands:
        logger.error("No commands discovered. Please check the commands directory.")
        sys.exit(1)
    
    # Create parser and parse arguments
    parser = router.create_parser()
    args = parser.parse_args()
    
    # Check if a command was provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute the command
    success = router.execute_command(args)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
