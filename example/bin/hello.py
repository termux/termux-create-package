#!/usr/bin/python3

class Hello:
    def hello(self):
        print("Hello World!")

class Main:
    def run(self):
        program = Hello()
        program.hello()

def main():
    main = Main()
    main.run()

if __name__ == "__main__":
    main()
