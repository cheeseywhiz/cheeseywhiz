import Data.List
import Data.Char
hash_init = 0xcbf29ce484222325
prime = 0x100000001b3

-- _to_bin :: Int -> [Int] -> [Int]
_to_bin 0 [] = [0]
_to_bin 0 bits = bits
_to_bin num bits = _to_bin (quot num 2) (bits ++ [if even num then 0 else 1])
to_bin num = _to_bin num []

-- from_little_endian :: Int -> [Int] -> Int
from_little_endian base digits = (
    sum
    (map
        (\ (index, digit) -> digit * (base ^ index))
        (zip [0..] digits)))
from_bin digits = from_little_endian 2 digits

-- repeat_n :: Int -> Int -> [Int]
repeat_n item n = map fst (zip (repeat item) [0..n])
-- list_fill :: [Int] -> Int -> Int -> [Int]
list_fill list item min_length = let diff = min_length - length list in
    let n_new_items = if diff < 0 then 0 else diff in
    list ++ repeat_n item n_new_items
-- zip_fill :: Int -> [Int] -> [Int] -> [(Int, Int)]
zip_fill item a b = let max_length = max (length a) (length b) in
    let new_a = list_fill a item max_length in
    let new_b = list_fill b item max_length in
    zip new_a new_b

-- int_xor :: (Integer, Integer) -> Integer
int_xor (p, q) = if (p == 0) /= (q == 0) then 1 else 0
-- bit_xor :: Integer -> Integer -> Integer
bit_xor p q = from_bin (map int_xor (zip_fill 0 (to_bin p) (to_bin q)))
-- mul_lsb :: Integer -> Integer -> Integer -> Integer
mul_lsb lsb a b = from_bin (take 64 (to_bin (a * b)))
mul_64 = mul_lsb 64
mul_prime = mul_64 prime
-- fnv_hash :: [Char] -> Integer
fnv_hash string = foldl (\ byte hash -> mul_prime (bit_xor byte hash)) hash_init (map ord string)

main = print (fnv_hash "hello world")
