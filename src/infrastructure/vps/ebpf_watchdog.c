/*
 * OMEGA CORE V4: EBPF WATCHDOG (XDP)
 * Status: PROTOTYPE | OMEGA_SECURITY | V4
 *
 * Verhindert API-Spam und überwacht ausgehende Verbindungen der Micro-VMs.
 */

#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include <bpf/bpf_helpers.h>

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);   // IP Address
    __type(value, __u64); // Last Call Timestamp
} api_call_tracker SEC(".maps");

SEC("xdp_watchdog")
int xdp_prog_main(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;

    struct ethhdr *eth = data;
    if (data + sizeof(*eth) > data_end)
        return XDP_PASS;

    if (eth->h_proto != __constant_htons(ETH_P_IP))
        return XDP_PASS;

    struct iphdr *iph = data + sizeof(*eth);
    if (data + sizeof(*eth) + sizeof(*iph) > data_end)
        return XDP_PASS;

    __u32 src_ip = iph->saddr;
    __u64 now = bpf_ktime_get_ns();

    __u64 *last_call = bpf_map_lookup_elem(&api_call_tracker, &src_ip);

    if (last_call) {
        // Limit: 1 Call pro 100ms (100,000,000 ns)
        if (now - *last_call < 100000000) {
            return XDP_DROP; // Rate Limit Veto
        }
    }

    bpf_map_update_elem(&api_call_tracker, &src_ip, &now, BPF_ANY);
    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
