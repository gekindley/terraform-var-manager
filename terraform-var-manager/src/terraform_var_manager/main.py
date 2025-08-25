"""
Main CLI interface for Terraform Variables Manager.
"""
import argparse
import logging
import sys

from .variable_manager import VariableManager
from .api_client import TerraformCloudError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Manage Terraform Cloud variables with advanced features",
        prog="terraform-var-manager"
    )
    
    parser.add_argument("--id", help="workspace id")
    parser.add_argument("--download", action="store_true", help="Download variables from workspace")
    parser.add_argument("--upload", action="store_true", help="Upload variables to workspace")
    parser.add_argument("--tfvars", help="path to the .tfvars file for upload")
    parser.add_argument(
        "--compare", 
        nargs=2, 
        metavar=("workspace1_id", "workspace2_id"),
        help="Compare variables between two workspaces"
    )
    parser.add_argument("--output", default="default.tfvars", help="Output file name")
    parser.add_argument(
        "--delete-all-variables", 
        action="store_true", 
        help="Delete all variables in the given workspace"
    )
    parser.add_argument(
        "--remove", 
        action="store_true", 
        help="Remove variables from remote that are not in tfvars"
    )
    
    return parser


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Initialize the variable manager
        manager = VariableManager()
        
        # Handle delete all variables operation
        if args.delete_all_variables:
            if not args.id:
                logger.error("--id is required when using --delete-all-variables")
                sys.exit(1)
            
            confirm = input(f"Are you sure you want to delete all variables from workspace \"{args.id}\"? (yes/[no]): ")
            if confirm.strip().lower() != "yes":
                logger.info("Operation aborted by user.")
                sys.exit(0)
            
            success = manager.delete_all_variables(args.id)
            sys.exit(0 if success else 1)
        
        # Handle download operation
        elif args.download:
            if not args.id:
                logger.error("--id is required when using --download")
                sys.exit(1)
            
            success = manager.download_variables(args.id, args.output)
            sys.exit(0 if success else 1)
        
        # Handle comparison operation
        elif args.compare:
            workspace1_id, workspace2_id = args.compare
            success = manager.compare_workspaces(workspace1_id, workspace2_id, args.output)
            sys.exit(0 if success else 1)
        
        # Handle upload operation
        elif args.upload:
            if not args.id:
                logger.error("--id is required when using --upload")
                sys.exit(1)
            
            if not args.tfvars:
                logger.error("Please specify the path to the .tfvars file using --tfvars.")
                sys.exit(1)
            
            success = manager.upload_variables(args.id, args.tfvars, args.remove)
            sys.exit(0 if success else 1)
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except TerraformCloudError as e:
        logger.error(f"Terraform Cloud API error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()