#!/usr/bin/env python3
"""
FastAPI JWT Template - Console Testing Application
A comprehensive test suite for testing all API endpoints
"""

import requests
import json
import time
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

class FastAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
        self.current_user = None
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"ℹ️  {message}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"⚠️  {message}")
    
    def show_auth_status(self):
        """Show current authentication status"""
        if self.current_user:
            print(f"🔐 Logged in as: {self.current_user}")
            print(f"   Access Token: {'✅ Valid' if self.access_token else '❌ None'}")
            print(f"   Refresh Token: {'✅ Valid' if self.refresh_token else '❌ None'}")
        else:
            print("🔓 Not authenticated - Please login or register first")
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """Make HTTP request and return response"""
        url = f"{self.base_url}{endpoint}"
        
        if headers is None:
            headers = {}
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "success": 200 <= response.status_code < 300
            }
        except requests.exceptions.ConnectionError:
            return {"status_code": 0, "data": {}, "success": False, "error": "Connection failed"}
        except Exception as e:
            return {"status_code": 0, "data": {}, "success": False, "error": str(e)}
    
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        self.print_header("Health Check Test")
        
        result = self.make_request("GET", "/health")
        
        if result["success"]:
            self.print_success("Health check passed")
            self.print_info(f"Status: {result['data'].get('status', 'unknown')}")
            return True
        else:
            self.print_error(f"Health check failed: {result.get('error', 'Unknown error')}")
            return False
    
    def test_root_endpoint(self) -> bool:
        """Test root endpoint"""
        self.print_header("Root Endpoint Test")
        
        result = self.make_request("GET", "/")
        
        if result["success"]:
            self.print_success("Root endpoint working")
            self.print_info(f"Message: {result['data'].get('msg', 'No message')}")
            return True
        else:
            self.print_error(f"Root endpoint failed: {result.get('error', 'Unknown error')}")
            return False
    
    def register_user(self, username: str, email: str, password: str) -> bool:
        """Register a new user"""
        self.print_header(f"User Registration: {username}")
        
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        result = self.make_request("POST", "/api/auth/register", data)
        
        if result["success"]:
            self.print_success(f"User {username} registered successfully")
            self.print_info(f"User ID: {result['data'].get('id', 'N/A')}")
            return True
        else:
            self.print_error(f"Registration failed: {result['data'].get('detail', 'Unknown error')}")
            return False
    
    def login_user(self, username: str, password: str) -> bool:
        """Login user and store tokens"""
        self.print_header(f"User Login: {username}")
        
        # Use form data for login
        url = f"{self.base_url}/api/auth/login"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(url, data=data)
            result = {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "success": 200 <= response.status_code < 300
            }
        except Exception as e:
            result = {"status_code": 0, "data": {}, "success": False, "error": str(e)}
        
        if result["success"]:
            self.access_token = result["data"].get("access_token")
            self.refresh_token = result["data"].get("refresh_token")
            self.current_user = username
            
            self.print_success(f"User {username} logged in successfully")
            self.print_info(f"Access token: {self.access_token[:20]}...")
            self.print_info(f"Refresh token: {self.refresh_token[:20]}...")
            return True
        else:
            self.print_error(f"Login failed: {result['data'].get('detail', 'Unknown error')}")
            return False
    
    def logout_user(self) -> bool:
        """Logout current user"""
        self.print_header("User Logout")
        
        result = self.make_request("POST", "/api/auth/logout")
        
        if result["success"]:
            self.print_success("Logout successful")
            self.access_token = None
            self.refresh_token = None
            self.current_user = None
            return True
        else:
            self.print_error(f"Logout failed: {result['data'].get('detail', 'Unknown error')}")
            return False
    
    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        self.print_header("Token Refresh")
        
        if not self.refresh_token:
            self.print_error("No refresh token available")
            return False
        
        # Send refresh token as query parameter instead of JSON data
        url = f"{self.base_url}/api/auth/refresh?refresh_token={self.refresh_token}"
        
        try:
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            response = requests.post(url, headers=headers)
            result = {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "success": 200 <= response.status_code < 300
            }
        except Exception as e:
            result = {"status_code": 0, "data": {}, "success": False, "error": str(e)}
        
        if result["success"]:
            self.access_token = result["data"].get("access_token")
            self.print_success("Access token refreshed successfully")
            self.print_info(f"New access token: {self.access_token[:20]}...")
            return True
        else:
            self.print_error(f"Token refresh failed: {result['data'].get('detail', 'Unknown error')}")
            return False
    
    def create_item(self, title: str, description: str = "") -> bool:
        """Create a new item"""
        if not self.current_user:
            self.print_warning("Please login first")
            return False
            
        self.print_header(f"Create Item: {title}")
        
        if not self.access_token:
            self.print_error("No access token available")
            return False
        
        data = {
            "title": title,
            "description": description
        }
        
        result = self.make_request("POST", "/api/items/", data)
        
        if result["success"]:
            self.print_success(f"Item '{title}' created successfully")
            self.print_info(f"Item ID: {result['data'].get('id', 'N/A')}")
            return True
        else:
            self.print_error(f"Item creation failed: {result['data'].get('detail', 'Unknown error')}")
            return False
    
    def get_items(self) -> bool:
        """Get list of all items"""
        if not self.current_user:
            self.print_warning("Please login first")
            return False
            
        self.print_header("Get All Items")
        
        if not self.access_token:
            self.print_error("No access token available")
            return False
        
        result = self.make_request("GET", "/api/items/")
        
        if result["success"]:
            items = result["data"]
            self.print_success(f"Retrieved {len(items)} items")
            if items:
                for item in items:
                    created_at = item.get('created_at', 'Unknown')
                    # Format the date if it's available
                    if created_at and created_at != 'Unknown':
                        try:
                            # Parse ISO format datetime and format it nicely
                            from datetime import datetime
                            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            formatted_date = created_at
                    else:
                        formatted_date = 'Unknown'
                    
                    self.print_info(f"ID: {item.get('id')} - {item.get('title')} - {item.get('description', 'No description')} - Created: {formatted_date}")
            else:
                self.print_info("No items found. Create some items first!")
            return True
        else:
            self.print_error(f"Failed to get items: {result['data'].get('detail', 'Unknown error')}")
            self.print_info(f"Status code: {result['status_code']}")
            return False
    
    def get_item(self, item_id: int) -> bool:
        """Get a specific item by ID"""
        if not self.current_user:
            self.print_warning("Please login first")
            return False
            
        self.print_header(f"Get Item: {item_id}")
        
        if not self.access_token:
            self.print_error("No access token available")
            return False
        
        result = self.make_request("GET", f"/api/items/{item_id}")
        
        if result["success"]:
            item = result["data"]
            created_at = item.get('created_at', 'Unknown')
            # Format the date if it's available
            if created_at and created_at != 'Unknown':
                try:
                    # Parse ISO format datetime and format it nicely
                    from datetime import datetime
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_date = created_at
            else:
                formatted_date = 'Unknown'
            
            self.print_success(f"Item retrieved successfully")
            self.print_info(f"ID: {item.get('id')} - {item.get('title')} - {item.get('description', 'No description')} - Created: {formatted_date}")
            return True
        else:
            self.print_error(f"Failed to get item: {result['data'].get('detail', 'Unknown error')}")
            return False
    
    def delete_item(self, item_id: int) -> bool:
        """Delete an item by ID"""
        if not self.current_user:
            self.print_warning("Please login first")
            return False
            
        self.print_header(f"Delete Item: {item_id}")
        
        if not self.access_token:
            self.print_error("No access token available")
            return False
        
        result = self.make_request("DELETE", f"/api/items/{item_id}")
        
        if result["success"]:
            self.print_success(f"Item {item_id} deleted successfully")
            return True
        else:
            self.print_error(f"Failed to delete item: {result['data'].get('detail', 'Unknown error')}")
            return False
    
    def run_comprehensive_test(self):
        """Run a comprehensive test of all endpoints"""
        self.print_header("Comprehensive Test Suite")
        
        # Test basic endpoints
        self.test_health_check()
        self.test_root_endpoint()
        
        # Test registration and login
        test_username = f"testuser_{int(time.time())}"
        test_email = f"{test_username}@example.com"
        test_password = "testpass123"
        
        if self.register_user(test_username, test_email, test_password):
            if self.login_user(test_username, test_password):
                # Test item operations
                self.create_item("Test Item 1", "This is a test item")
                self.create_item("Test Item 2", "Another test item")
                self.get_items()
                
                # Test token refresh
                self.refresh_access_token()
                
                # Test logout
                self.logout_user()
        
        self.print_header("Comprehensive Test Complete")
    
    def require_auth(self) -> bool:
        """Check if user is authenticated, prompt for login if not"""
        if not self.current_user:
            self.print_warning("Authentication required!")
            print("\nOptions:")
            print("1. Login with existing account")
            print("2. Register new account")
            print("3. Cancel")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == "1":
                username = input("Enter username: ").strip()
                password = input("Enter password: ").strip()
                return self.login_user(username, password)
            elif choice == "2":
                username = input("Enter username: ").strip()
                email = input("Enter email: ").strip()
                password = input("Enter password: ").strip()
                if self.register_user(username, email, password):
                    return self.login_user(username, password)
                return False
            else:
                return False
        
        return True

def main():
    """Main function to run the test application"""
    print("="*60)
    print(" FastAPI JWT Template - Console Testing Application")
    print("="*60)
    
    # Get API base URL
    base_url = input("Enter API base URL (default: http://localhost:8000): ").strip()
    if not base_url:
        base_url = "http://localhost:8000"
    
    tester = FastAPITester(base_url)
    
    while True:
        tester.clear_screen()
        # Show authentication status at the top
        print("\n" + "="*60)
        tester.show_auth_status()
        print("="*60)
        
        print("\n TEST MENU")
        print("="*60)
        print("1. Run Comprehensive Test Suite")
        print("2. Test Health Check")
        print("3. Test User Registration")
        print("4. Test User Login")
        print("5. Test Item Creation")
        print("6. Test Item Listing")
        print("7. Test Item Deletion")
        print("8. Test Token Refresh")
        print("9. Test User Logout")
        print("10. Interactive Mode")
        print("11. Show Current Status")
        print("0. Exit")
        
        choice = input("\nSelect an option (0-11): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            tester.run_comprehensive_test()
            input("\nPress Enter to continue...")
        elif choice == "2":
            tester.test_health_check()
            input("\nPress Enter to continue...")
        elif choice == "3":
            username = input("Enter username: ").strip()
            email = input("Enter email: ").strip()
            password = input("Enter password: ").strip()
            tester.register_user(username, email, password)
            input("\nPress Enter to continue...")
        elif choice == "4":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            tester.login_user(username, password)
            input("\nPress Enter to continue...")
        elif choice == "5":
            if tester.require_auth():
                title = input("Enter item title: ").strip()
                description = input("Enter item description (optional): ").strip()
                tester.create_item(title, description)
                input("\nPress Enter to continue...")
        elif choice == "6":
            if tester.require_auth():
                tester.get_items()
                # If no items found, offer to create a test item
                if not tester.current_user:
                    return
                # This is a simple check - in practice, you'd want to check the actual response
                print("\n💡 Tip: If no items are shown, try creating some items first using option 5!")
                input("\nPress Enter to continue...")
        elif choice == "7":
            if tester.require_auth():
                item_id = input("Enter item ID to delete: ").strip()
                if item_id.isdigit():
                    tester.delete_item(int(item_id))
                else:
                    tester.print_error("Invalid item ID")
                input("\nPress Enter to continue...")
        elif choice == "8":
            if tester.require_auth():
                tester.refresh_access_token()
                input("\nPress Enter to continue...")
        elif choice == "9":
            if tester.current_user:
                tester.logout_user()
            else:
                tester.print_warning("No user logged in")
            input("\nPress Enter to continue...")
        elif choice == "10":
            run_interactive_mode(tester)
        elif choice == "11":
            show_current_status(tester)
            input("\nPress Enter to continue...")
        else:
            print("Invalid option. Please try again.")
            input("\nPress Enter to continue...")

def show_current_status(tester: FastAPITester):
    """Show current status of the tester"""
    tester.print_header("Current Status")
    tester.show_auth_status()
    
    if tester.current_user:
        print(f"\nBase URL: {tester.base_url}")
        print(f"Session active: ✅")

def run_interactive_mode(tester: FastAPITester):
    """Run interactive mode for testing"""
    tester.print_header("Interactive Mode")
    
    if not tester.require_auth():
        tester.print_warning("Authentication required for interactive mode")
        return
    
    print("Interactive mode started. Type 'help' for commands, 'exit' to quit.")
    
    while True:
        try:
            command = input(f"\n[{tester.current_user}]> ").strip().lower()
            
            if command == "exit" or command == "quit":
                break
            elif command == "help":
                print("\nAvailable commands:")
                print("  create <title> [description] - Create new item")
                print("  list - List all items")
                print("  get <id> - Get specific item")
                print("  delete <id> - Delete item")
                print("  refresh - Refresh access token")
                print("  logout - Logout current user")
                print("  status - Show current status")
                print("  exit/quit - Exit interactive mode")
            elif command.startswith("create "):
                parts = command.split(" ", 2)
                if len(parts) >= 2:
                    title = parts[1]
                    description = parts[2] if len(parts) > 2 else ""
                    tester.create_item(title, description)
                else:
                    tester.print_error("Usage: create <title> [description]")
            elif command.startswith("list"):
                tester.get_items()
            elif command.startswith("get "):
                parts = command.split()
                if len(parts) > 1 and parts[1].isdigit():
                    tester.get_item(int(parts[1]))
                else:
                    tester.print_error("Usage: get <id>")
            elif command.startswith("delete "):
                parts = command.split()
                if len(parts) > 1 and parts[1].isdigit():
                    tester.delete_item(int(parts[1]))
                else:
                    tester.print_error("Usage: delete <id>")
            elif command == "refresh":
                tester.refresh_access_token()
            elif command == "logout":
                if tester.logout_user():
                    tester.print_info("Logged out. Interactive mode ended.")
                    break
            elif command == "status":
                show_current_status(tester)
            else:
                print("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\nExiting interactive mode...")
            break
        except Exception as e:
            tester.print_error(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 