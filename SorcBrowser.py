import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from urllib.parse import urljoin
from collections import deque

# Initialize console
console = Console()

# ASCII art with onion (like Tor Browser)
ASCII_ART = r"""
                      ::::::::      :::     ::::    :::  :::::::: 
                    :+:    :+:   :+: :+:   :+:+:   :+: :+:    :+: 
                   +:+         +:+   +:+  :+:+:+  +:+ +:+         
                  :#:        +#++:++#++: +#+ +:+ +#+ :#:          
                 +#+   +#+# +#+     +#+ +#+  +#+#+# +#+   +#+#    
                #+#    #+# #+#     #+# #+#   #+#+# #+#    #+#     
               ########  ###     ### ###    ####  ########       
                      ::::::::  :::    ::: ::::::::::: ::::::::  
                    :+:    :+: :+:    :+:     :+:    :+:    :+:  
                   +:+    +:+ +:+    +:+     +:+    +:+          
                  +#+    +:+ +#+    +:+     +#+    :#:           
                 +#+    +#+ +#+    +#+     +#+    +#+   +#+#     
                #+#    #+# #+#    #+#     #+#    #+#    #+#      
               ########   ########      ###    ########         
"""

def fetch_url(url, proxies=None):
    """Fetches HTML content from the specified URL using proxies."""
    try:
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Request error: {e}[/bold red]")
        return None

def parse_html(html, base_url):
    """Parses HTML and extracts text and links."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract text
    text_content = soup.get_text()
    
    # Extract links
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)  # Convert relative URLs to absolute
        link_text = link.text.strip() or full_url  # Use URL if link text is empty
        links.append((link_text, full_url))
    
    return text_content, links

def display_content(text, links, current_url):
    """Displays text content and links in a table."""
    # Display current URL
    console.print(Panel.fit(f"[bold cyan]Current page:[/bold cyan] [yellow]{current_url}[/yellow]"))
    
    # Display text content
    console.print(Panel.fit(Text(text, justify="left"), title="[bold green]Page Content[/bold green]"))
    
    # Display links in a table
    if links:
        table = Table(title="[bold blue]Page Links[/bold blue]", show_header=True, header_style="bold magenta")
        table.add_column("#", justify="right", style="cyan", no_wrap=True)
        table.add_column("Link Text", style="green")
        table.add_column("URL", style="yellow")
        
        for i, (text, url) in enumerate(links, start=1):
            table.add_row(str(i), text, url)
        
        console.print(table)

def display_tabs(tabs, active_tab):
    """Displays the list of tabs."""
    table = Table(title="[bold blue]Tabs[/bold blue]", show_header=True, header_style="bold magenta")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("URL", style="yellow")
    
    for tab_id, tab_data in tabs.items():
        url = tab_data["current_url"] or "New Tab"
        if tab_id == active_tab:
            url = f"[bold green]{url}[/bold green]"
        table.add_row(str(tab_id), url)
    
    console.print(table)

def display_history(history):
    """Displays browsing history."""
    if not history:
        console.print("[bold red]History is empty![/bold red]")
        return
    
    table = Table(title="[bold blue]Browsing History[/bold blue]", show_header=True, header_style="bold magenta")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("URL", style="yellow")
    
    for i, url in enumerate(reversed(history), start=1):
        table.add_row(str(i), url)
    
    console.print(table)

def main():
    """Main program loop."""
    # Display ASCII art with onion
    console.print(ASCII_ART, style="bold green")
    console.print("Welcome to SorcBrowser!", style="bold green")
    console.print("=" * 50, style="bold cyan")
    
    tabs = {}  # Dictionary to store tabs
    tab_counter = 1  # Counter for tab IDs
    active_tab = None  # Active tab
    proxies = None  # Default proxies
    
    while True:
        if not tabs:
            # If no tabs exist, create the first one
            tabs[tab_counter] = {
                "current_url": None,
                "history": deque(),
                "content": None,
                "links": []
            }
            active_tab = tab_counter
            tab_counter += 1
        
        # Clear console before displaying new state
        console.clear()
        
        # Display active tab
        console.print(Panel.fit(f"[bold cyan]Active Tab: {active_tab}[/bold cyan]"))
        
        # Display list of tabs
        display_tabs(tabs, active_tab)
        
        # Get data for the active tab
        current_tab_data = tabs[active_tab]
        current_url = current_tab_data["current_url"]
        history = current_tab_data["history"]
        links = current_tab_data["links"]
        
        # Display content of the active tab
        if current_tab_data["content"]:
            display_content(current_tab_data["content"], links, current_url)
        
        # Action menu
        console.print("\n[bold]Choose an action:[/bold]")
        console.print("1. Follow a link")
        console.print("2. Go back")
        console.print("3. Enter a new URL")
        console.print("4. Create a new tab")
        console.print("5. Switch to a tab")
        console.print("6. Close a tab")
        console.print("7. View history")
        console.print("8. Set proxy")
        console.print("9. Exit")
        choice = console.input("[bold]Your choice: [/bold]")
        
        if choice == '1':
            if not links:
                console.print("[bold red]No links on this page![/bold red]")
                console.input("\nPress Enter to continue...")
                continue
            while True:
                link_number = console.input("[bold]Enter link number: [/bold]")
                if link_number.isdigit():
                    link_number = int(link_number)
                    if 1 <= link_number <= len(links):
                        url = links[link_number - 1][1]  # Get the selected link's URL
                        break
                    else:
                        console.print("[bold red]Invalid link number![/bold red]")
                else:
                    console.print("[bold red]Enter a number![/bold red]")
        elif choice == '2':
            if history:
                url = history.pop()  # Go back to the previous page
            else:
                console.print("[bold red]History is empty![/bold red]")
                console.input("\nPress Enter to continue...")
                continue
        elif choice == '3':
            while True:
                url = console.input("[bold]Enter a new URL: [/bold]")
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                if fetch_url(url, proxies):  # Check if the URL is accessible
                    break
                else:
                    console.print("[bold red]Invalid URL![/bold red]")
        elif choice == '4':
            # Create a new tab
            tabs[tab_counter] = {
                "current_url": None,
                "history": deque(),
                "content": None,
                "links": []
            }
            active_tab = tab_counter
            tab_counter += 1
            continue
        elif choice == '5':
            # Switch to a tab
            tab_id = console.input("[bold]Enter tab ID: [/bold]")
            if tab_id.isdigit():
                tab_id = int(tab_id)
                if tab_id in tabs:
                    active_tab = tab_id
                else:
                    console.print("[bold red]Tab not found![/bold red]")
            else:
                console.print("[bold red]Enter a number![/bold red]")
            console.input("\nPress Enter to continue...")
            continue
        elif choice == '6':
            # Close a tab
            if len(tabs) == 1:
                console.print("[bold red]Cannot close the last tab![/bold red]")
                console.input("\nPress Enter to continue...")
                continue
            tab_id = console.input("[bold]Enter tab ID to close: [/bold]")
            if tab_id.isdigit():
                tab_id = int(tab_id)
                if tab_id in tabs:
                    del tabs[tab_id]
                    if active_tab == tab_id:
                        active_tab = next(iter(tabs))  # Switch to the first tab
                else:
                    console.print("[bold red]Tab not found![/bold red]")
            else:
                console.print("[bold red]Enter a number![/bold red]")
            console.input("\nPress Enter to continue...")
            continue
        elif choice == '7':
            # View history
            display_history(history)
            console.input("\nPress Enter to continue...")
            continue
        elif choice == '8':
            # Set proxy
            proxy_url = console.input("[bold]Enter proxy (e.g., http://proxy.example.com:8080): [/bold]")
            if proxy_url:
                proxies = {
                    "http": proxy_url,
                    "https": proxy_url,
                }
                console.print(f"[bold green]Proxy set: {proxy_url}[/bold green]")
            else:
                proxies = None
                console.print("[bold green]Proxy disabled.[/bold green]")
            console.input("\nPress Enter to continue...")
            continue
        elif choice == '9':
            break
        else:
            console.print("[bold red]Invalid choice![/bold red]")
            console.input("\nPress Enter to continue...")
            continue
        
        # Fetch and parse the page
        html = fetch_url(url, proxies)
        if html:
            if current_url:
                history.append(current_url)  # Save the current URL to history
            current_tab_data["current_url"] = url
            text_content, links = parse_html(html, url)
            current_tab_data["content"] = text_content
            current_tab_data["links"] = links
        else:
            console.input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()