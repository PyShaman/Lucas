def prime_numbers_in_interval(lower, upper):
    for num in range(lower, upper + 1):
        if num > 1:
            for i in range(2, num):
                if (num % i) == 0:
                    break
            else:
                print(f"{num}", end=", ")


def decimal_to_sum_binary(dec):
    l = dec
    sum = 0
    while l > 0:
        p = l
        p = p % 2
        l = l // 2
        sum += p
    return sum


def main():
    prime_numbers_in_interval(1, 100)
    # sito(2, 1000)
    # sito(100, 10000)
    # sito(1000, 100000)


if __name__ == '__main__':
    main()
