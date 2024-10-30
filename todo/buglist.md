
# Critical

(Impossible to use the application.)

# Bad

(Breaks core functionality, but possible workarounds)

- [x] Running `python ./main -s -r -w` gets stuck in a loop
    - **Cause**
        - Flask apps restart the entire script when the server needs to refresh (for some reason). This causes the *search* and *rank* operations to fire every time the user interacts with teh web app
    - **Work Around**
        - Do not run `main -s -r -w` in one command. 
        - Instead run `main -s -r` and then run `main -w` 
        in seperate commands
    - **Fix**
        - [ ] Learn how flask actually works. 
        - [ ] Make sure only relevant scripts fire on
        server refresh. 

# Moderate

(Annoying, requries workarounds for some functionality)

# Minor

(Does not break functionality)