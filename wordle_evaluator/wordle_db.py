def main():
    with CONFIG_PATH.open("r", encoding="utf8") as f:
        cfg = yaml.safe_load(f)


if __name__ == "__main__":
    main()
