from django.core.management.base import BaseCommand

import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = (
        "Demonstrate pandas/numpy operations: create 10x3 DataFrame, filter by values, "
        "filter with two-column conditions and select two columns, replace values, "
        "and append another dummy DataFrame with same columns."
    )

    def add_arguments(self, parser):
        parser.add_argument("--size", type=int, default=10, help="Row count for the base DataFrame (default: 10)")
        parser.add_argument("--threshold", type=int, default=50, help="Threshold for single-column filter on A (default: 50)")
        parser.add_argument("--threshold_a", type=int, default=60, help="Threshold for A in two-column filter (default: 60)")
        parser.add_argument("--threshold_b", type=int, default=60, help="Threshold for B in two-column filter (default: 60)")
        parser.add_argument("--replace_lt", type=int, default=20, help="Replace values in C less than this (default: 20)")
        parser.add_argument("--replace_with", type=int, default=0, help="Replacement value for C (default: 0)")
        parser.add_argument("--append_rows", type=int, default=5, help="Rows in the second dummy DataFrame to append (default: 5)")

    def handle(self, *args, **opts):
        size = opts["size"]
        threshold = opts["threshold"]
        ta = opts["threshold_a"]
        tb = opts["threshold_b"]
        replace_lt = opts["replace_lt"]
        replace_with = opts["replace_with"]
        append_rows = opts["append_rows"]

        # Seed for reproducibility
        np.random.seed(42)

        # 1) Create DataFrame (10x3 by default) from a dictionary of lists (via numpy)
        data = {
            "A": np.random.randint(0, 100, size).tolist(),
            "B": np.random.randint(0, 100, size).tolist(),
            "C": np.random.randint(0, 100, size).tolist(),
        }
        df = pd.DataFrame(data)
        self.stdout.write(self.style.NOTICE("Base DataFrame (10x3):"))
        self.stdout.write(df.to_string(index=False))

        # 2) Filter DataFrame based on value greater than some value and print (column A > threshold)
        df_gt = df[df["A"] > threshold]
        self.stdout.write(self.style.NOTICE(f"\nFilter: A > {threshold}"))
        self.stdout.write(df_gt.to_string(index=False))

        # 3) Filter DataFrame with two columns and print (A > ta AND B > tb)
        df_two_cond = df[(df["A"] > ta) & (df["B"] > tb)]
        self.stdout.write(self.style.NOTICE(f"\nFilter with two-column conditions: A > {ta} AND B > {tb}"))
        self.stdout.write(df_two_cond.to_string(index=False))

        # Also show selecting two columns only
        df_two_cols = df[["A", "B"]]
        self.stdout.write(self.style.NOTICE("\nSelect only two columns (A, B):"))
        self.stdout.write(df_two_cols.to_string(index=False))

        # 4) Replace values within DataFrame and print (in column C)
        df_replaced = df.copy()
        df_replaced.loc[df_replaced["C"] < replace_lt, "C"] = replace_with
        self.stdout.write(self.style.NOTICE(f"\nReplace: C values < {replace_lt} with {replace_with}"))
        self.stdout.write(df_replaced.to_string(index=False))

        # 5) Append two DataFrames (same columns) and print shape and tail
        other_data = {
            "A": np.random.randint(0, 100, append_rows).tolist(),
            "B": np.random.randint(0, 100, append_rows).tolist(),
            "C": np.random.randint(0, 100, append_rows).tolist(),
        }
        df2 = pd.DataFrame(other_data)
        combined = pd.concat([df, df2], ignore_index=True)
        self.stdout.write(self.style.NOTICE(f"\nAppend another DataFrame with {append_rows} rows"))
        self.stdout.write(self.style.SUCCESS(f"Combined shape: {combined.shape}"))
        self.stdout.write(self.style.NOTICE("Combined tail:"))
        self.stdout.write(combined.tail(append_rows).to_string(index=False))